"""
Hospital Patient Portal - Configuration Module
===============================================
This module contains all configuration settings for the Flask application.
Sensitive values are loaded from environment variables for security.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with default settings."""
    
    # Flask Core Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///hospital.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Security Settings
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # RSA Key Paths
    PRIVATE_KEY_PATH = os.environ.get('PRIVATE_KEY_PATH') or 'keys/private_key.pem'
    PUBLIC_KEY_PATH = os.environ.get('PUBLIC_KEY_PATH') or 'keys/public_key.pem'
    
    # RSA Key Size (4096 bits for strong security)
    RSA_KEY_SIZE = 4096
    
    # Gemini AI API Key
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # File Upload Settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'dcm'}
    
    # Password Hashing Settings
    BCRYPT_LOG_ROUNDS = 12
    
    # SMTP Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'baveshchowdary1@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'cshc oqyu jrrn kvnb'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'baveshchowdary1@gmail.com'
    
    # OTP Settings
    OTP_EXPIRY_MINUTES = 10
    OTP_LENGTH = 6
    
    # Blockchain Configuration (Ganache)
    GANACHE_URL = os.environ.get('GANACHE_URL') or 'http://127.0.0.1:7545'
    CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
    BLOCKCHAIN_PRIVATE_KEY = os.environ.get('BLOCKCHAIN_PRIVATE_KEY')
    BLOCKCHAIN_ENABLED = os.environ.get('BLOCKCHAIN_ENABLED', 'true').lower() == 'true'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration with enhanced security."""
    DEBUG = False
    FLASK_ENV = 'production'
    SESSION_COOKIE_SECURE = True  # Require HTTPS
    

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
