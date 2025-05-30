from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

class User(db.Model, UserMixin):
    """User model for authentication and user management"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    profile_image = db.Column(db.String(120), default='default_profile.jpg')
    about_me = db.Column(db.Text)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    reset_token = db.Column(db.String(100))
    reset_token_expiration = db.Column(db.DateTime)
    
    # Relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, first_name=None, last_name=None):
        self.username = username
        self.email = email
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
    
    def set_password(self, password):
        """Set password hash from plain text password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_seen(self):
        """Update the last seen timestamp"""
        self.last_seen = datetime.utcnow()
        db.session.commit()
    
    def get_full_name(self):
        """Return user's full name or username if not available"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader function"""
    return User.query.get(int(user_id))
