#!/usr/bin/env python3
"""
Standalone migration script to avoid circular imports
"""
import os
import sys
from flask import Flask
from flask_migrate import Migrate
from models import db
from config import Config

# Create a minimal Flask app for migrations
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        # Import models to ensure they're registered
        from models import User, Subject, Chapter, Quiz, Question, Score
        
        # Create tables if they don't exist
        db.create_all()
        print("Database tables created/updated successfully!") 