from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from app import db
from app.models.post import Post, Comment, Tag
from app.forms.post import PostForm, CommentForm
from app.utils.file_utils import save_picture, delete_file

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    """Create a new post"""
    form = PostForm()
    
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id,
            published=form.published.data
        )
        
        # Handle image upload
        if form.image.data:
            image_file = save_picture(form.image.data, folder='post_images')
            post.image_file = image_file
        
        # Handle tags
        if form.tags.data:
            tag_names = [tag.strip() for tag in form.tags.data.split(',')]
            for tag_name in tag_names:
                if tag_name:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                    post.tags.append(tag)
        
        db.session.add(post)
        db.session.commit()
        
        flash('Your post has been created!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    
    return render_template('posts/create_post.html', title='New Post', 
                          form=form, legend='New Post')


@posts_bp.route('/post/<int:post_id>')
def post(post_id):
    """View a specific post"""
    post = Post.query.get_or_404(post_id)
    
    # If post is not published, only author can view it
    if not post.published and (not current_user.is_authenticated or current_user.id != post.user_id):
        abort(404)
    
    form = CommentForm()
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()
    
    # Get similar posts based on content similarity
    similar_posts = Post.get_similar_posts(post_id, limit=3)
    
    return render_template('posts/post.html', title=post.title, 
                          post=post, form=form, comments=comments,
                          similar_posts=similar_posts)


@posts_bp.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    """Update an existing post"""
    post = Post.query.get_or_404(post_id)
    
    # Check if current user is the author
    if post.user_id != current_user.id:
        abort(403)
    
    form = PostForm()
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.published = form.published.data
        
        # Handle image upload
        if form.image.data:
            # Delete old image if exists
            if post.image_file:
                delete_file(post.image_file)
            
            image_file = save_picture(form.image.data, folder='post_images')
            post.image_file = image_file
        
        # Handle tags
        # Remove all existing tags
        post.tags = []
        
        # Add new tags
        if form.tags.data:
            tag_names = [tag.strip() for tag in form.tags.data.split(',')]
            for tag_name in tag_names:
                if tag_name:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                    post.tags.append(tag)
        
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.published.data = post.published
        form.tags.data = ', '.join([tag.name for tag in post.tags])
    
    return render_template('posts/create_post.html', title='Update Post', 
                          form=form, legend='Update Post', post=post)


@posts_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete a post"""
    post = Post.query.get_or_404(post_id)
    
    # Check if current user is the author
    if post.user_id != current_user.id:
        abort(403)
    
    # Delete post image if exists
    if post.image_file:
        delete_file(post.image_file)
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))


@posts_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add a comment to a post"""
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            post_id=post.id,
            user_id=current_user.id
        )
        
        # Analyze sentiment of the comment
        comment.analyze_sentiment()
        
        db.session.add(comment)
        db.session.commit()
        
        # Flash different messages based on sentiment
        sentiment_messages = {
            'positive': 'Your positive comment has been added! 😊',
            'negative': 'Your comment has been added, though it seems negative. 😞',
            'neutral': 'Your comment has been added! 😐'
        }
        flash(sentiment_messages.get(comment.sentiment, 'Your comment has been added!'), 'success')
    
    return redirect(url_for('posts.post', post_id=post.id))


@posts_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Delete a comment"""
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if current user is the author of the comment or the post
    if comment.user_id != current_user.id and comment.post.user_id != current_user.id:
        abort(403)
    
    post_id = comment.post_id
    
    db.session.delete(comment)
    db.session.commit()
    
    flash('Comment has been deleted!', 'success')
    return redirect(url_for('posts.post', post_id=post_id))


@posts_bp.route('/user/<string:username>/posts')
def user_posts(username):
    """View all posts by a specific user"""
    from app.models.user import User
    
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    
    # If current user is the author, show all posts including unpublished
    if current_user.is_authenticated and current_user.id == user.id:
        posts = Post.query.filter_by(user_id=user.id).order_by(
            Post.created_at.desc()
        ).paginate(page=page, per_page=5)
    else:
        # Otherwise show only published posts
        posts = Post.query.filter_by(
            user_id=user.id, published=True
        ).order_by(Post.created_at.desc()).paginate(page=page, per_page=5)
    
    return render_template('posts/user_posts.html', posts=posts, 
                          user=user, title=f'Posts by {username}')


@posts_bp.route('/recommendations')
@login_required
def recommendations():
    """Show personalized post recommendations for the current user"""
    # Get recommendations for the current user
    recommended_posts = Post.get_recommendations_for_user(current_user.id, limit=5)
    
    # Build the recommendation model if it doesn't exist
    from app.utils.ai.recommendation import should_rebuild_model, build_recommendation_model
    if should_rebuild_model():
        all_posts = Post.query.filter_by(published=True).all()
        build_recommendation_model(all_posts)
    
    return render_template('posts/recommendations.html', 
                          title='Recommended Posts',
                          posts=recommended_posts)
