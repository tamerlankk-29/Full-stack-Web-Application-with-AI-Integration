import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(test_config=None):
    """Application factory function"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure the app
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URI', 'sqlite:///app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER', 'app/static/uploads'),
        MAX_CONTENT_LENGTH=int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)),  # 16MB max upload
    )

    if test_config:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Ensure upload folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profile_pics'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'post_images'), exist_ok=True)
    
    # Check if default profile image exists and has content
    default_profile_path = os.path.join(app.config['UPLOAD_FOLDER'], 'default_profile.jpg')
    if not os.path.exists(default_profile_path) or os.path.getsize(default_profile_path) < 100:
            # Create a basic default profile image or copy from a template
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (150, 150), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        d.ellipse((10, 10, 140, 140), fill=(255, 255, 255))
        img.save(default_profile_path)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    csrf.init_app(app)
    
    from app.utils.context_processors import inject_now
    app.context_processor(inject_now)

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.posts import posts_bp
    from app.routes.errors import errors_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(errors_bp)

    @app.shell_context_processor
    def make_shell_context():
        from app.models.user import User
        from app.models.post import Post
        return {'db': db, 'User': User, 'Post': Post}

    with app.app_context():
        db.create_all()

    return app
