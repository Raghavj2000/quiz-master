import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "your_secret_key_here"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_VERIFY_SUB = False
    CORS_HEADERS = "Content-Type"
    
    # Daily reminder configuration
    DAILY_REMINDER_HOUR = 21  # or whatever hour it is now
    DAILY_REMINDER_MINUTE = 51  # or 2 minutes from current minute