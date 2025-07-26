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
        
        # Check if created_at column exists in quiz table
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('quiz')]
        
        if 'created_at' not in columns:
            print("Adding created_at column to quiz table...")
            # Add created_at column
            db.engine.execute("ALTER TABLE quiz ADD COLUMN created_at DATETIME")
            # Set default value for existing records
            db.engine.execute("UPDATE quiz SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
            print("created_at column added successfully!")
        else:
            print("created_at column already exists in quiz table.")
        
        print("Database migration completed successfully!") 