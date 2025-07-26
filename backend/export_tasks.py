from celery import shared_task
from models import db, Score, Quiz, Chapter, Subject, User
from sqlalchemy import func, desc
from datetime import datetime
import csv
import io
import os

@shared_task(bind=True)
def export_user_quiz_data(self, user_id, filters=None):
    """
    Celery task to export user quiz data
    """
    try:
        # Update task state
        self.update_state(state='PROGRESS', meta={'status': 'Generating CSV data...'})
        
        # Generate CSV data
        csv_content = generate_quiz_csv_data(user_id, filters)
        
        # Update task state
        self.update_state(state='PROGRESS', meta={'status': 'Export completed'})
        
        return {
            'status': 'SUCCESS',
            'csv_content': csv_content,
            'filename': f"user_export_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            'message': 'Export completed successfully'
        }
        
    except Exception as e:
        return {
            'status': 'FAILURE',
            'error': str(e),
            'message': 'Export failed'
        }

@shared_task(bind=True)
def export_admin_quiz_data(self, user_id, filters=None):
    """
    Celery task to export admin quiz data
    """
    try:
        # Update task state
        self.update_state(state='PROGRESS', meta={'status': 'Generating CSV data...'})
        
        # Generate CSV data
        csv_content = generate_admin_csv_data(filters)
        
        # Update task state
        self.update_state(state='PROGRESS', meta={'status': 'Export completed'})
        
        return {
            'status': 'SUCCESS',
            'csv_content': csv_content,
            'filename': f"admin_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            'message': 'Export completed successfully'
        }
        
    except Exception as e:
        return {
            'status': 'FAILURE',
            'error': str(e),
            'message': 'Export failed'
        }

def generate_quiz_csv_data(user_id, filters=None):
    """Generate CSV data for user's quiz details"""
    # Base query to get quiz details
    query = db.session.query(
        Score.id.label('score_id'),
        Score.quiz_id,
        Score.user_id,
        Score.total_scored,
        Score.total_questions,
        Score.timestamp,
        Quiz.name.label('quiz_name'),
        Quiz.date_of_quiz,
        Quiz.time_duration,
        Quiz.remarks,
        Chapter.id.label('chapter_id'),
        Chapter.name.label('chapter_name'),
        Subject.id.label('subject_id'),
        Subject.name.label('subject_name'),
        User.username,
        User.full_name
    ).join(
        Quiz, Score.quiz_id == Quiz.id
    ).join(
        Chapter, Quiz.chapter_id == Chapter.id
    ).join(
        Subject, Chapter.subject_id == Subject.id
    ).join(
        User, Score.user_id == User.id
    ).filter(
        Score.user_id == user_id
    )
    
    # Add date filters if provided
    if filters:
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        
        if start_date:
            query = query.filter(Score.timestamp >= start_date)
        if end_date:
            query = query.filter(Score.timestamp <= end_date)
    
    # Order by timestamp descending
    query = query.order_by(Score.timestamp.desc())
    results = query.all()
    
    # Create CSV data
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    
    # Write header
    csv_writer.writerow([
        'Score ID', 'Quiz ID', 'User ID', 'Username', 'Full Name',
        'Subject ID', 'Subject Name', 'Chapter ID', 'Chapter Name',
        'Quiz Name', 'Total Scored', 'Total Questions', 'Percentage Score',
        'Quiz Date', 'Quiz Duration', 'Quiz Remarks', 'Attempt Timestamp'
    ])
    
    # Write data rows
    for row in results:
        percentage = round((row.total_scored / row.total_questions * 100), 2) if row.total_questions > 0 else 0
        
        csv_writer.writerow([
            row.score_id, row.quiz_id, row.user_id, row.username,
            row.full_name or '', row.subject_id, row.subject_name,
            row.chapter_id, row.chapter_name, row.quiz_name,
            row.total_scored, row.total_questions, f"{percentage}%",
            row.date_of_quiz.strftime('%Y-%m-%d') if row.date_of_quiz else '',
            str(row.time_duration) if row.time_duration else '',
            row.remarks or '',
            row.timestamp.strftime('%Y-%m-%d %H:%M:%S') if row.timestamp else ''
        ])
    
    return csv_data.getvalue()

def generate_admin_csv_data(filters=None):
    """Generate CSV data for admin export"""
    # Base query for all quiz details
    query = db.session.query(
        Score.id.label('score_id'),
        Score.quiz_id,
        Score.user_id,
        Score.total_scored,
        Score.total_questions,
        Score.timestamp,
        Quiz.name.label('quiz_name'),
        Quiz.date_of_quiz,
        Quiz.time_duration,
        Quiz.remarks,
        Chapter.id.label('chapter_id'),
        Chapter.name.label('chapter_name'),
        Subject.id.label('subject_id'),
        Subject.name.label('subject_name'),
        User.username,
        User.full_name
    ).join(
        Quiz, Score.quiz_id == Quiz.id
    ).join(
        Chapter, Quiz.chapter_id == Chapter.id
    ).join(
        Subject, Chapter.subject_id == Subject.id
    ).join(
        User, Score.user_id == User.id
    )
    
    # Apply filters
    if filters:
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        subject_id = filters.get('subject_id')
        user_id = filters.get('user_id')
        
        if start_date:
            query = query.filter(Score.timestamp >= start_date)
        if end_date:
            query = query.filter(Score.timestamp <= end_date)
        if subject_id:
            query = query.filter(Subject.id == subject_id)
        if user_id:
            query = query.filter(User.id == user_id)
    
    # Order by timestamp descending
    query = query.order_by(Score.timestamp.desc())
    results = query.all()
    
    # Create CSV data
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    
    # Write header
    csv_writer.writerow([
        'Score ID', 'Quiz ID', 'User ID', 'Username', 'Full Name',
        'Subject ID', 'Subject Name', 'Chapter ID', 'Chapter Name',
        'Quiz Name', 'Total Scored', 'Total Questions', 'Percentage Score',
        'Quiz Date', 'Quiz Duration', 'Quiz Remarks', 'Attempt Timestamp'
    ])
    
    # Write data rows
    for row in results:
        percentage = round((row.total_scored / row.total_questions * 100), 2) if row.total_questions > 0 else 0
        
        csv_writer.writerow([
            row.score_id, row.quiz_id, row.user_id, row.username,
            row.full_name or '', row.subject_id, row.subject_name,
            row.chapter_id, row.chapter_name, row.quiz_name,
            row.total_scored, row.total_questions, f"{percentage}%",
            row.date_of_quiz.strftime('%Y-%m-%d') if row.date_of_quiz else '',
            str(row.time_duration) if row.time_duration else '',
            row.remarks or '',
            row.timestamp.strftime('%Y-%m-%d %H:%M:%S') if row.timestamp else ''
        ])
    
    return csv_data.getvalue() 