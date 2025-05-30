import os
import secrets
from PIL import Image
from flask import current_app

def save_picture(form_picture, folder='uploads', size=(800, 800)):
    """
    Save uploaded picture with a random name and resize it
    
    Args:
        form_picture: The uploaded file from form
        folder: Subfolder within UPLOAD_FOLDER to save to
        size: Tuple of (width, height) to resize image to
        
    Returns:
        String: Filename of the saved picture
    """
    # Generate random filename to avoid collisions
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_ext
    
    # Create full path for saving
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_folder, exist_ok=True)
    picture_path = os.path.join(upload_folder, picture_filename)
    
    # Resize and save image
    img = Image.open(form_picture)
    img.thumbnail(size)
    img.save(picture_path)
    
    # Return only the filename without the folder prefix
    # This is because templates use url_for('static', filename='uploads/' + path)
    return picture_filename


def allowed_file(filename, allowed_extensions=None):
    """
    Check if a filename has an allowed extension
    
    Args:
        filename: The filename to check
        allowed_extensions: Set of allowed extensions (default: images)
        
    Returns:
        Boolean: True if file is allowed, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def delete_file(filename):
    """
    Delete a file from the upload folder
    
    Args:
        filename: Relative path of file to delete
        
    Returns:
        Boolean: True if deleted successfully, False otherwise
    """
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"Error deleting file: {e}")
    return False
