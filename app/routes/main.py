from flask import Blueprint, render_template, request, current_app
from app.models.post import Post, Tag
from app.forms.post import SearchForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
def home():
    """Home page route"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(published=True).order_by(
        Post.created_at.desc()
    ).paginate(page=page, per_page=5)
    
    return render_template('main/home.html', posts=posts, title='Home')

@main_bp.route('/about')
def about():
    """About page route"""
    return render_template('main/about.html', title='About')

@main_bp.route('/search')
def search():
    """Search for posts"""
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    
    if not query:
        return render_template('main/search.html', title='Search', form=SearchForm())
    
    # Search in title, content, and tags
    # First get posts that match title or content
    base_query = Post.query.filter(
        (Post.title.contains(query) | 
         Post.content.contains(query)) &
        Post.published == True
    )
    
    # Also search for posts with matching tags
    tag_query = Post.query.join(Post.tags).filter(
        Post.published == True,
        Tag.name.contains(query)
    )
    
    # Combine the results and remove duplicates
    combined_query = base_query.union(tag_query)
    
    # Apply pagination
    posts = combined_query.order_by(Post.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return render_template(
        'main/search_results.html',
        title=f'Search Results for "{query}"',
        posts=posts,
        query=query,
        form=SearchForm(query=query)
    )

@main_bp.route('/tag/<string:tag_name>')
def tag_posts(tag_name):
    """Show posts with specific tag"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    
    posts = tag.posts.filter_by(published=True).order_by(
        Post.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    return render_template(
        'main/tag_posts.html',
        title=f'Posts tagged with "{tag_name}"',
        posts=posts,
        tag=tag,
        per_page=per_page
    )
