from app import create_app, db

# Create app context
app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database initialized successfully!")
