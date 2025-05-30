"""
Content recommendation module for recommending posts to users.
Uses a TF-IDF vectorizer and cosine similarity to find similar posts.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
from datetime import datetime, timedelta

# Constants
MODEL_PATH = 'app/utils/ai/models'
VECTORIZER_FILE = 'tfidf_vectorizer.joblib'
FEATURES_FILE = 'tfidf_features.joblib'
POST_IDS_FILE = 'post_ids.joblib'
MODEL_EXPIRY_DAYS = 1  # Rebuild model if older than this many days

def ensure_model_directory():
    """Ensure the model directory exists"""
    os.makedirs(MODEL_PATH, exist_ok=True)

def get_model_path(filename):
    """Get the full path to a model file"""
    return os.path.join(MODEL_PATH, filename)

def should_rebuild_model():
    """Check if the model should be rebuilt"""
    vectorizer_path = get_model_path(VECTORIZER_FILE)
    
    # If model doesn't exist, rebuild
    if not os.path.exists(vectorizer_path):
        return True
    
    # Check if model is older than MODEL_EXPIRY_DAYS
    model_time = datetime.fromtimestamp(os.path.getmtime(vectorizer_path))
    return datetime.now() - model_time > timedelta(days=MODEL_EXPIRY_DAYS)

def build_recommendation_model(posts):
    """
    Build the recommendation model using TF-IDF vectorization.
    
    Args:
        posts (list): List of Post objects
        
    Returns:
        tuple: (vectorizer, features, post_ids)
    """
    ensure_model_directory()
    
    # Extract text and IDs
    documents = []
    post_ids = []
    
    for post in posts:
        # Combine title and content for better recommendations
        text = f"{post.title} {post.content}"
        documents.append(text)
        post_ids.append(post.id)
    
    # Create and fit vectorizer
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        min_df=2,
        ngram_range=(1, 2)
    )
    
    # If no documents, return empty model
    if not documents:
        return vectorizer, np.array([]), []
    
    # Transform documents to TF-IDF features
    features = vectorizer.fit_transform(documents)
    
    # Save the model
    joblib.dump(vectorizer, get_model_path(VECTORIZER_FILE))
    joblib.dump(features, get_model_path(FEATURES_FILE))
    joblib.dump(post_ids, get_model_path(POST_IDS_FILE))
    
    return vectorizer, features, post_ids

def load_recommendation_model():
    """
    Load the recommendation model.
    
    Returns:
        tuple: (vectorizer, features, post_ids) or None if model doesn't exist
    """
    try:
        vectorizer = joblib.load(get_model_path(VECTORIZER_FILE))
        features = joblib.load(get_model_path(FEATURES_FILE))
        post_ids = joblib.load(get_model_path(POST_IDS_FILE))
        return vectorizer, features, post_ids
    except (FileNotFoundError, EOFError):
        return None, None, None

def get_similar_posts(post_id, num_recommendations=3):
    """
    Get similar posts based on content similarity.

    Args:
        post_id (int): The ID of the post to find similar posts for
        num_recommendations (int): Number of recommendations to return

    Returns:
        list: List of post IDs of similar posts
    """
    # Load the model
    vectorizer, features, post_ids = load_recommendation_model()
    
    # If model doesn't exist or post_id not in post_ids, return empty list
    if vectorizer is None or features is None or post_ids is None:
        return []
    
    try:
        # Find the index of the post
        post_index = post_ids.index(post_id)
    except ValueError:
        # Post not in model
        return []
    
    # Get the feature vector for the post
    post_vector = features[post_index:post_index+1]
    
    # Calculate similarity with all other posts
    similarities = cosine_similarity(post_vector, features).flatten()
    
    # Get indices of similar posts (excluding the post itself)
    similar_indices = similarities.argsort()[:-num_recommendations-2:-1]
    
    # Filter out the post itself
    similar_indices = [i for i in similar_indices if i != post_index]
    
    # Get post IDs of similar posts
    similar_post_ids = [post_ids[i] for i in similar_indices]
    
    return similar_post_ids

def get_user_recommendations(user_id, posts, num_recommendations=5):
    """
    Get personalized recommendations for a user based on their reading history.
    
    Args:
        user_id (int): The ID of the user
        posts (list): List of all Post objects
        num_recommendations (int): Number of recommendations to return
        
    Returns:
        list: List of recommended Post objects
    """
    from app.models.post import Post
    from app import db
    
    # Get posts the user has commented on
    user_commented_posts = db.session.query(Post.id).join(
        Post.comments
    ).filter_by(user_id=user_id).all()
    
    user_commented_post_ids = [p[0] for p in user_commented_posts]
    
    # If user hasn't commented on any posts, return most recent posts
    if not user_commented_post_ids:
        return Post.query.filter_by(published=True).order_by(
            Post.created_at.desc()
        ).limit(num_recommendations).all()
    
    # Get recommendations for each post the user has commented on
    recommended_post_ids = set()
    for post_id in user_commented_post_ids:
        similar_post_ids = get_similar_posts(post_id, num_recommendations=2)
        recommended_post_ids.update(similar_post_ids)
    
    # Remove posts the user has already commented on
    recommended_post_ids = recommended_post_ids - set(user_commented_post_ids)
    
    # If we don't have enough recommendations, add recent posts
    if len(recommended_post_ids) < num_recommendations:
        recent_posts = Post.query.filter_by(published=True).filter(
            ~Post.id.in_(user_commented_post_ids)
        ).order_by(Post.created_at.desc()).limit(
            num_recommendations - len(recommended_post_ids)
        ).all()
        
        recommended_post_ids.update([p.id for p in recent_posts])
    
    # Get the actual post objects
    recommended_posts = Post.query.filter(
        Post.id.in_(recommended_post_ids),
        Post.published == True
    ).order_by(Post.created_at.desc()).limit(num_recommendations).all()
    
    return recommended_posts
