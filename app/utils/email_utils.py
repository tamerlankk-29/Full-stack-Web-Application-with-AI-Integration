import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import url_for, current_app

def send_email(subject, recipient, html_body):
    """
    Send an email using SMTP
    
    In a production environment, you would use a proper email service.
    This is a simplified version for demonstration purposes.
    """
    # For demonstration purposes only - in a real app, use environment variables
    sender_email = os.environ.get('EMAIL_USER', 'noreply@example.com')
    password = os.environ.get('EMAIL_PASSWORD', '')
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.example.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    
    # Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient
    
    # Add HTML content
    html_part = MIMEText(html_body, "html")
    message.attach(html_part)
    
    # For development, just print the email content instead of sending
    print(f"Would send email to {recipient}:")
    print(f"Subject: {subject}")
    print(f"Body: {html_body}")
    
    # For development, we'll return True to simulate successful email sending
    return True

def send_reset_email(user):
    """Send password reset email to user"""
    # Create reset URL with token
    reset_url = url_for('auth.reset_password', token=user.reset_token, _external=True)
    
    # Create email content
    subject = "Password Reset Request"
    html_body = f'''
    <html>
    <body>
        <h2>Password Reset Request</h2>
        <p>Hello {user.get_full_name()},</p>
        <p>To reset your password, visit the following link:</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>This link will expire in 1 hour.</p>
        <p>If you did not make this request, simply ignore this email and no changes will be made.</p>
    </body>
    </html>
    '''
    
    # Send the email
    return send_email(subject, user.email, html_body)
