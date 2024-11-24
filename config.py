#config.py
from datetime import timedelta
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET', 'fallback_secret_key')
    JWT_REFRESH_SECRET_KEY = os.getenv('REFRESH_SECRET_KEY', 'fallback_refresh_secret_key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('ACCESS_TOKEN_EXPIRES', 3600)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('REFRESH_TOKEN_EXPIRES', 604800)))

    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'your_email@example.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'your_email_password')
    RESET_PASSWORD_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv('RESET_PASSWORD_TOKEN_EXPIRES', 30)))

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_DISCOVERY_URL = os.getenv("GOOGLE_DISCOVERY_URL")
    GOOGLE_DISCOVERY_URL = os.getenv("GOOGLE_DISCOVERY_URL")
    GOOGLE_AUTH_BASE_URL = os.getenv("GOOGLE_AUTH_BASE_URL")
    GOOGLE_TOKEN_URL = os.getenv("GOOGLE_TOKEN_URL")
    GOOGLE_USER_INFO_URL = os.getenv("GOOGLE_USER_INFO_URL")

    API_KEY = os.getenv("API_KEY")
    BASE_URL = os.getenv("BASE_URL")
