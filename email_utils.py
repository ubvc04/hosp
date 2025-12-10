"""
Hospital Patient Portal - Email Utilities
==========================================
SMTP email functionality for sending OTP codes.
"""

import random
import string
import traceback
from datetime import datetime, timedelta
from flask import current_app, render_template_string
from flask_mail import Mail, Message

mail = Mail()


def init_mail(app):
    """Initialize Flask-Mail with the app."""
    mail.init_app(app)
    # Log mail configuration for debugging
    app.logger.info(f"Mail configured: Server={app.config.get('MAIL_SERVER')}, Port={app.config.get('MAIL_PORT')}")


def generate_otp(length=6):
    """Generate a random numeric OTP."""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(to_email, otp_code, user_name="User"):
    """
    Send OTP email for password reset.
    
    Args:
        to_email: Recipient email address
        otp_code: The OTP code to send
        user_name: Name of the user
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        current_app.logger.info(f"Attempting to send OTP email to {to_email}")
        
        subject = "Password Reset OTP - Hospital Patient Portal"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 500px;
                    margin: 0 auto;
                    background: #ffffff;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .header p {{
                    margin: 10px 0 0;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 40px 30px;
                    text-align: center;
                }}
                .greeting {{
                    color: #333;
                    font-size: 18px;
                    margin-bottom: 20px;
                }}
                .message {{
                    color: #666;
                    font-size: 16px;
                    line-height: 1.6;
                    margin-bottom: 30px;
                }}
                .otp-box {{
                    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
                    border: 3px dashed #667eea;
                    border-radius: 15px;
                    padding: 25px;
                    margin: 30px 0;
                }}
                .otp-code {{
                    font-size: 42px;
                    font-weight: bold;
                    letter-spacing: 12px;
                    color: #667eea;
                    font-family: 'Courier New', monospace;
                }}
                .warning {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 0 10px 10px 0;
                    text-align: left;
                }}
                .warning p {{
                    margin: 0;
                    color: #856404;
                    font-size: 14px;
                }}
                .expiry {{
                    color: #dc3545;
                    font-weight: 600;
                    font-size: 14px;
                    margin-top: 20px;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    border-top: 1px solid #e9ecef;
                }}
                .footer p {{
                    margin: 0;
                    color: #6c757d;
                    font-size: 12px;
                }}
                .icon {{
                    font-size: 50px;
                    margin-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="icon">🏥</div>
                    <h1>Hospital Patient Portal</h1>
                    <p>Password Reset Request</p>
                </div>
                <div class="content">
                    <p class="greeting">Hello, <strong>{user_name}</strong>!</p>
                    <p class="message">
                        We received a request to reset your password. 
                        Use the OTP code below to verify your identity and set a new password.
                    </p>
                    <div class="otp-box">
                        <div class="otp-code">{otp_code}</div>
                    </div>
                    <p class="expiry">⏱️ This code expires in {current_app.config.get('OTP_EXPIRY_MINUTES', 10)} minutes</p>
                    <div class="warning">
                        <p>⚠️ <strong>Security Notice:</strong> If you didn't request this password reset, 
                        please ignore this email. Your password will remain unchanged.</p>
                    </div>
                </div>
                <div class="footer">
                    <p>© 2024 Hospital Patient Portal. All rights reserved.</p>
                    <p>This is an automated message. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text alternative
        text_body = f"""
        Hospital Patient Portal - Password Reset
        =========================================
        
        Hello, {user_name}!
        
        We received a request to reset your password.
        
        Your OTP Code: {otp_code}
        
        This code expires in {current_app.config.get('OTP_EXPIRY_MINUTES', 10)} minutes.
        
        If you didn't request this password reset, please ignore this email.
        
        - Hospital Patient Portal Team
        """
        
        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[to_email]
        )
        msg.body = text_body
        msg.html = html_body
        
        current_app.logger.info(f"Sending email from {current_app.config['MAIL_USERNAME']} to {to_email}")
        mail.send(msg)
        current_app.logger.info(f"OTP email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send OTP email: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return False


def send_password_changed_email(to_email, user_name="User"):
    """
    Send confirmation email after password change.
    
    Args:
        to_email: Recipient email address
        user_name: Name of the user
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        subject = "✅ Password Changed Successfully - Hospital Patient Portal"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 500px;
                    margin: 0 auto;
                    background: #ffffff;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .content {{
                    padding: 40px 30px;
                    text-align: center;
                }}
                .success-icon {{
                    font-size: 60px;
                    margin-bottom: 20px;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔒 Password Changed</h1>
                </div>
                <div class="content">
                    <div class="success-icon">✅</div>
                    <p>Hello, <strong>{user_name}</strong>!</p>
                    <p>Your password has been successfully changed.</p>
                    <p>If you didn't make this change, please contact support immediately.</p>
                </div>
                <div class="footer">
                    <p>© 2024 Hospital Patient Portal</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            sender=(current_app.config.get('MAIL_SENDER_NAME', 'Hospital Portal'), 
                   current_app.config['MAIL_USERNAME']),
            recipients=[to_email]
        )
        msg.html = html_body
        
        mail.send(msg)
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send password changed email: {str(e)}")
        return False
