"""
Update database script to add AI-related fields to the database.
Run this script to update the database schema after adding the AI integration.
This script uses SQLite directly to avoid dependency issues.
"""
import sqlite3
import os

def update_database():
    # Path to the SQLite database
    db_path = 'instance/app.db'
    
    # Check if the database exists
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Please run the application first to create the database.")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if sentiment columns already exist
    cursor.execute("PRAGMA table_info(comments)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Add sentiment columns if they don't exist
    if 'sentiment' not in columns:
        print("Adding sentiment columns to comments table...")
        
        # SQLite doesn't support adding multiple columns in a single ALTER TABLE statement
        cursor.execute('ALTER TABLE comments ADD COLUMN sentiment VARCHAR(20) DEFAULT "neutral"')
        cursor.execute('ALTER TABLE comments ADD COLUMN sentiment_polarity FLOAT DEFAULT 0.0')
        cursor.execute('ALTER TABLE comments ADD COLUMN sentiment_subjectivity FLOAT DEFAULT 0.0')
        
        conn.commit()
        print("Added sentiment columns to comments table.")
    else:
        print("Sentiment columns already exist in comments table.")
    
    # Close the connection
    conn.close()
    print("Database update complete!")
    print("\nNOTE: The sentiment analysis for existing comments will be performed when the application runs.")
    print("The recommendation models will be built automatically when needed.")

if __name__ == '__main__':
    print("Updating database for AI integration...")
    update_database()
