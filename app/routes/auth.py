from datetime import datetime, timedelta
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse

from app import db
from app.models.user import User
from app.forms.auth import (
    RegistrationForm, LoginForm, UpdateProfileForm,
    PasswordResetRequestForm, PasswordResetForm
)
from app.utils.file_utils import save_picture
from app.utils.email_utils import send_reset_email

auth_bp = Blueprint('auth', __name__)

SESSION_TIMEOUT = 30 * 60

@auth_bp.before_request
def check_session_timeout():
    """Check if user session has timed out"""
    if current_user.is_authenticated:
        last_active = session.get('last_active')
        
        session['last_active'] = datetime.utcnow().timestamp()
        
        if last_active and datetime.utcnow().timestamp() - last_active > SESSION_TIMEOUT:
            logout_user()
            flash('Your session has expired. Please login again.', 'info')
            return redirect(url_for('auth.login'))
        
        if not last_active or datetime.utcnow().timestamp() - last_active > 300:  # 5 minutes
            current_user.update_last_seen()


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            session['last_active'] = datetime.utcnow().timestamp()
            
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('main.home')
            
            flash('Login successful!', 'success')
            return redirect(next_page)
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    
    return render_template('auth/login.html', title='Login', form=form)


@auth_bp.route('/logout')
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile route"""
    form = UpdateProfileForm(current_user.username, current_user.email)
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.about_me = form.about_me.data
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('auth.profile'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.about_me.data = current_user.about_me
    
    return render_template('auth/profile.html', title='Profile', form=form)


@auth_bp.route('/profile/picture', methods=['POST'])
@login_required
def update_profile_picture():
    """Update user profile picture"""
    if 'profile_picture' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('auth.profile'))
    
    file = request.files['profile_picture']
    
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('auth.profile'))
    
    if file:
        try:
            picture_file = save_picture(file, folder='profile_pics', size=(150, 150))
            current_user.profile_image = picture_file
            db.session.commit()
            flash('Your profile picture has been updated!', 'success')
        except Exception as e:
            flash(f'Error updating profile picture: {str(e)}', 'danger')
    
    return redirect(url_for('auth.profile'))


@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    """Request password reset route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generate token
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # Send email
            send_reset_email(user)
        
        # Always show this message even if email not found (security)
        flash('If your email exists in our database, you will receive a password reset link.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_request.html', title='Reset Password', form=form)


@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # Find user with this token
    user = User.query.filter_by(reset_token=token).first()
    
    # Check if token is valid and not expired
    if not user or not user.reset_token_expiration or user.reset_token_expiration < datetime.utcnow():
        flash('Invalid or expired token. Please request a new password reset.', 'warning')
        return redirect(url_for('auth.reset_password_request'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_token = None
        user.reset_token_expiration = None
        db.session.commit()
        
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='Reset Password', form=form)
