# Suppress Pydantic warnings from Google Generative AI library
import warnings
warnings.filterwarnings("ignore", message="Field name.*shadows an attribute in parent")

"""
Hospital Patient Portal - Main Application
==========================================
Flask application factory and entry point.

ARCHITECTURE:
-------------
1. Application Factory Pattern for testability
2. Blueprint registration for modular routes
3. Security headers and error handlers
4. Database and crypto initialization

SECURITY FEATURES:
-----------------
- CSRF protection
- Secure session cookies
- Security headers (CSP, X-Frame-Options, etc.)
- Input validation
- Rate limiting
- Brute force protection
"""

import os
from flask import Flask, render_template, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_app(config_name=None):
    """
    Application factory function.
    
    Args:
        config_name: Configuration to use ('development', 'production', 'testing')
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Initialize database
    from models import init_db
    init_db(app)
    
    # Initialize Flask-Mail for email functionality
    from email_utils import init_mail
    init_mail(app)
    
    # Initialize authentication
    from auth import init_auth, auth_bp
    init_auth(app)
    
    # Initialize cryptography
    from crypto_utils import init_crypto
    init_crypto(app)
    
    # Initialize security features
    from security import init_security
    init_security(app)
    
    # Initialize AI suggestions
    from ai_suggestions import init_suggestion_engine
    init_suggestion_engine(app.config.get('GEMINI_API_KEY'))
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    
    from admin_routes import admin_bp
    app.register_blueprint(admin_bp)
    
    from patient_routes import patient_bp
    app.register_blueprint(patient_bp)
    
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        """Add security headers to every response."""
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS filter
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (adjust for production)
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
        )
        
        return response
    
    # Root route
    @app.route('/')
    def index():
        """Redirect to login page."""
        return redirect(url_for('auth.login'))
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        from models import db
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Template context processors
    @app.context_processor
    def inject_now():
        """Inject current datetime into templates."""
        from datetime import datetime
        return {'now': datetime.utcnow()}
    
    # Custom Jinja filters
    @app.template_filter('datetime')
    def format_datetime(value, format='%B %d, %Y'):
        """Format datetime objects."""
        if value is None:
            return ''
        return value.strftime(format)
    
    @app.template_filter('currency')
    def format_currency(value):
        """Format numbers as currency."""
        if value is None:
            return '$0.00'
        return f'${value:,.2f}'
    
    return app


# Create the application instance
app = create_app()


if __name__ == '__main__':
    # Run the development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
