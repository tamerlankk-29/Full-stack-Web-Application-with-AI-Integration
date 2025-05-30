from flask import Blueprint, render_template

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(404)
def error_404(error):
    """Handle 404 Not Found errors"""
    return render_template('errors/404.html', title='Page Not Found'), 404

@errors_bp.app_errorhandler(403)
def error_403(error):
    """Handle 403 Forbidden errors"""
    return render_template('errors/403.html', title='Forbidden'), 403

@errors_bp.app_errorhandler(500)
def error_500(error):
    """Handle 500 Internal Server Error"""
    return render_template('errors/500.html', title='Server Error'), 500
