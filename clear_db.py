"""
Script to clear all posts and user accounts from the database.
This will delete ALL data - use with caution!
"""
import os
import sqlite3
from app import create_app, db
from app.models.user import User
from app.models.post import Post, Comment, Tag

def clear_database_with_orm():
    """Clear database using SQLAlchemy ORM"""
    print("Clearing database using SQLAlchemy ORM...")
    app = create_app()
    
    with app.app_context():
        # Delete all comments first (they depend on posts and users)
        comment_count = Comment.query.count()
        Comment.query.delete()
        
        # Delete all post-tag associations and tags
        tag_count = Tag.query.count()
        Tag.query.delete()
        
        # Delete all posts
        post_count = Post.query.count()
        Post.query.delete()
        
        # Delete all users
        user_count = User.query.count()
        User.query.delete()
        
        # Commit the changes
        db.session.commit()
        
        print(f"Deleted {comment_count} comments")
        print(f"Deleted {tag_count} tags")
        print(f"Deleted {post_count} posts")
        print(f"Deleted {user_count} users")
        print("Database cleared successfully!")

def clear_database_with_sqlite():
    """Clear database using direct SQLite commands"""
    print("Clearing database using direct SQLite commands...")
    db_path = 'instance/app.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Disable foreign key constraints temporarily
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    # Delete data from all relevant tables
    tables = ['comments', 'post_tags', 'tags', 'posts', 'users']
    
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"Cleared table: {table}")
        except sqlite3.Error as e:
            print(f"Error clearing table {table}: {e}")
    
    # Re-enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database cleared successfully!")

def clear_uploaded_files():
    """Clear uploaded images"""
    print("Clearing uploaded files...")
    
    # Paths to clear
    upload_paths = [
        'app/static/uploads/profile_pics',
        'app/static/uploads/post_images'
    ]
    
    # Default profile image to keep
    default_profile = 'app/static/uploads/default_profile.jpg'
    
    for path in upload_paths:
        if os.path.exists(path):
            file_count = 0
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                # Skip default profile image
                if file_path == default_profile:
                    continue
                
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        file_count += 1
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
            
            print(f"Deleted {file_count} files from {path}")
    
    print("Uploaded files cleared!")

if __name__ == "__main__":
    print("WARNING: This will delete ALL posts, comments, tags, and user accounts!")
    confirmation = input("Type 'YES' to confirm: ")
    
    if confirmation.upper() == "YES":
        try:
            # Try using ORM first
            clear_database_with_orm()
        except Exception as e:
            print(f"Error using ORM: {e}")
            print("Falling back to direct SQLite commands...")
            clear_database_with_sqlite()
        
        # Clear uploaded files
        clear_uploaded_files()
        
        print("All data has been cleared successfully!")
    else:
        print("Operation cancelled.")
