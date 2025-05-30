# Flask Full-Stack Web Application

A complete web application built with Flask that includes user authentication, CRUD operations, file uploads, and more. This project demonstrates end-to-end implementation of a dynamic, interactive, secure, and data-driven web application.

## Features

- **User Authentication System**
  - Registration with validation
  - Secure login with password hashing
  - Profile management
  - Password reset functionality
  - Remember me functionality

- **Session Management**
  - Session timeout (30 minutes)
  - Auto-logout for inactive users
  - Secure session handling

- **Database Operations**
  - SQLAlchemy ORM integration
  - Normalized database design
  - Relationships (one-to-many, many-to-many)
  - JOINs for related data

- **CRUD Operations**
  - Create, Read, Update, Delete for posts
  - Comment system
  - Tag management

- **Form Handling**
  - WTForms validation
  - CSRF protection
  - Custom validators
  - Error handling

- **File Uploads**
  - Image uploads for posts and profiles
  - Secure file handling
  - File type validation

- **Search Functionality**
  - Search in post titles and content
  - Tag-based filtering
  - Pagination of results

- **Modern Architecture**
  - Blueprint-based modular design
  - Object-oriented programming principles
  - Separation of concerns

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Set up environment variables:
   ```
   copy .env.example .env
   ```
   Then edit the `.env` file to set your SECRET_KEY and other configuration options
6. Initialize the database:
   ```
   python init_db.py
   ```
7. Run the application:
   ```
   python app.py
   ```
   or
   ```
   flask run
   ```

## Usage

1. Register a new account at `/register`
2. Log in with your credentials at `/login`
3. Create new posts at `/post/new`
4. View your profile and update information at `/profile`
5. Search for posts using the search bar
6. Browse posts by tags
7. Add comments to posts

## Project Structure

```
├── app/                 # Main application package
│   ├── __init__.py      # Application factory
│   ├── models/          # Database models
│   │   ├── user.py      # User model
│   │   └── post.py      # Post, Comment, and Tag models
│   ├── routes/          # Blueprint routes
│   │   ├── main.py      # Main routes (home, search)
│   │   ├── auth.py      # Authentication routes
│   │   ├── posts.py     # Post CRUD operations
│   │   └── errors.py    # Error handlers
│   ├── static/          # Static files
│   │   ├── css/         # CSS files
│   │   ├── js/          # JavaScript files
│   │   └── uploads/     # User uploads
│   ├── templates/       # Jinja2 templates
│   │   ├── auth/        # Authentication templates
│   │   ├── errors/      # Error pages
│   │   ├── main/        # Main page templates
│   │   └── posts/       # Post templates
│   ├── forms/           # WTForms classes
│   │   ├── auth.py      # Authentication forms
│   │   └── post.py      # Post and comment forms
│   └── utils/           # Helper functions
│       ├── file_utils.py # File handling utilities
│       └── email_utils.py # Email utilities
├── app.py               # Application entry point
├── init_db.py           # Database initialization script
├── requirements.txt     # Project dependencies
└── .env                 # Environment variables
```

## Database Schema

### Users Table
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- first_name
- last_name
- profile_image
- about_me
- last_seen
- created_at
- is_active
- reset_token
- reset_token_expiration

### Posts Table
- id (Primary Key)
- title
- content
- image_file
- created_at
- updated_at
- published
- user_id (Foreign Key to Users)

### Comments Table
- id (Primary Key)
- content
- created_at
- post_id (Foreign Key to Posts)
- user_id (Foreign Key to Users)

### Tags Table
- id (Primary Key)
- name (Unique)

### Post_Tags Association Table
- post_id (Foreign Key to Posts)
- tag_id (Foreign Key to Tags)

## Technologies Used

- **Backend**
  - Python 3.x
  - Flask 2.2.3
  - SQLAlchemy 2.0.15
  - Flask-Login 0.6.2
  - Flask-WTF 1.1.1
  - Werkzeug 2.2.3
  - Pillow 9.5.0
  - python-dotenv 1.0.0

- **Frontend**
  - HTML5
  - CSS3
  - Bootstrap 5
  - Jinja2 3.1.2

- **Database**
  - SQLite (development)
  - Can be configured for MySQL/PostgreSQL (production)

## Security Features

- Password hashing with Werkzeug
- CSRF protection with Flask-WTF
- Secure file uploads
- Session timeout
- Form validation
- Error handling

## Future Enhancements

- API endpoints for mobile applications
- Social authentication (OAuth)
- Advanced search with filters
- User roles and permissions
- Email notifications
- Real-time chat functionality
