from datetime import datetime
from app import db

# Tags association table for many-to-many relationship
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Post(db.Model):
    """Post model for blog posts or other content"""
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published = db.Column(db.Boolean, default=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))
    
    def __init__(self, title, content, user_id, image_file=None, published=True):
        self.title = title
        self.content = content
        self.user_id = user_id
        self.image_file = image_file
        self.published = published
    
    def add_tag(self, tag):
        """Add a tag to the post"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag):
        """Remove a tag from the post"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def __repr__(self):
        return f'<Post {self.title}>'
        
    @staticmethod
    def get_similar_posts(post_id, limit=3):
        """Get similar posts based on content similarity"""
        from app.utils.ai.recommendation import get_similar_posts
        from app import db
        
        similar_post_ids = get_similar_posts(post_id, num_recommendations=limit)
        
        if not similar_post_ids:
            # If no recommendations, return recent posts
            return Post.query.filter_by(published=True).filter(
                Post.id != post_id
            ).order_by(Post.created_at.desc()).limit(limit).all()
        
        # Get the actual post objects
        similar_posts = Post.query.filter(
            Post.id.in_(similar_post_ids),
            Post.published == True
        ).all()
        
        return similar_posts
        
    @staticmethod
    def get_recommendations_for_user(user_id, limit=5):
        """Get personalized recommendations for a user"""
        from app.utils.ai.recommendation import get_user_recommendations
        from app import db
        
        # Get all published posts for the recommendation engine
        all_posts = Post.query.filter_by(published=True).all()
        
        # Get recommendations
        return get_user_recommendations(user_id, all_posts, num_recommendations=limit)


class Comment(db.Model):
    """Comment model for post comments"""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Sentiment analysis fields
    sentiment = db.Column(db.String(20), default='neutral')
    sentiment_polarity = db.Column(db.Float, default=0.0)
    sentiment_subjectivity = db.Column(db.Float, default=0.0)
    
    # Foreign keys
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    
    def analyze_sentiment(self):
        """Analyze the sentiment of the comment content"""
        from app.utils.ai.sentiment_analysis import analyze_sentiment
        
        result = analyze_sentiment(self.content)
        self.sentiment = result['sentiment']
        self.sentiment_polarity = result['polarity']
        self.sentiment_subjectivity = result['subjectivity']
    
    def get_sentiment_emoji(self):
        """Get an emoji representing the sentiment"""
        from app.utils.ai.sentiment_analysis import get_sentiment_emoji
        return get_sentiment_emoji(self.sentiment)
    
    def __repr__(self):
        return f'<Comment {self.id}>'


class Tag(db.Model):
    """Tag model for categorizing posts"""
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return f'<Tag {self.name}>'
