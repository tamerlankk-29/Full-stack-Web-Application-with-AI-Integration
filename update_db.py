import sqlite3
import os
from pathlib import Path

# Get the absolute path to the database file
db_path = Path(__file__).parent / 'instance' / 'app.db'

print(f"Attempting to update database at: {db_path}")

# Connect to the SQLite database
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the columns already exist
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Add reset_token column if it doesn't exist
    if 'reset_token' not in columns:
        print("Adding reset_token column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token VARCHAR(100)")
    else:
        print("reset_token column already exists.")
    
    # Add reset_token_expiration column if it doesn't exist
    if 'reset_token_expiration' not in columns:
        print("Adding reset_token_expiration column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expiration TIMESTAMP")
    else:
        print("reset_token_expiration column already exists.")
    
    # Commit the changes
    conn.commit()
    print("Database update completed successfully!")
    
except sqlite3.Error as e:
    print(f"SQLite error: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
