import os
from datetime import timedelta

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    
    # Database config
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///woodnook.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload config
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    
    # Pagination
    PRODUCTS_PER_PAGE = 12
    ORDERS_PER_PAGE = 20
    
    # Payment config (demo)
    STRIPE_PUBLISHABLE_KEY = 'pk_test_demo'
    STRIPE_SECRET_KEY = 'sk_test_demo'
    
    # Email config (for future use)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # App info
    APP_NAME = "WoodNook"
    APP_DESCRIPTION = "Handcrafted Wooden Toys & Décor"
    APP_VERSION = "1.0.0"
