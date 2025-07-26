from flask import Blueprint, request, jsonify, send_file
from models import db, Score, Quiz, Chapter, Subject, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime
import csv
import io
import os

export_bp = Blueprint('export_bp', __name__)

def generate_quiz_csv_data(user_id, start_date=None, end_date=None):
    """
    Generate CSV data for user's quiz details
    """
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
    if start_date:
        query = query.filter(Score.timestamp >= start_date)
    if end_date:
        query = query.filter(Score.timestamp <= end_date)
    
    # Order by timestamp descending (most recent first)
    query = query.order_by(Score.timestamp.desc())
    
    results = query.all()
    
    # Create CSV data
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    
    # Write header
    csv_writer.writerow([
        'Score ID',
        'Quiz ID',
        'User ID',
        'Username',
        'Full Name',
        'Subject ID',
        'Subject Name',
        'Chapter ID',
        'Chapter Name',
        'Quiz Name',
        'Total Scored',
        'Total Questions',
        'Percentage Score',
        'Quiz Date',
        'Quiz Duration',
        'Quiz Remarks',
        'Attempt Timestamp'
    ])
    
    # Write data rows
    for row in results:
        percentage = round((row.total_scored / row.total_questions * 100), 2) if row.total_questions > 0 else 0
        
        csv_writer.writerow([
            row.score_id,
            row.quiz_id,
            row.user_id,
            row.username,
            row.full_name or '',
            row.subject_id,
            row.subject_name,
            row.chapter_id,
            row.chapter_name,
            row.quiz_name,
            row.total_scored,
            row.total_questions,
            f"{percentage}%",
            row.date_of_quiz.strftime('%Y-%m-%d') if row.date_of_quiz else '',
            str(row.time_duration) if row.time_duration else '',
            row.remarks or '',
            row.timestamp.strftime('%Y-%m-%d %H:%M:%S') if row.timestamp else ''
        ])
    
    return csv_data.getvalue()

@export_bp.route('/export/user/<int:user_id>/quiz-details', methods=['POST'])
@jwt_required()
def export_user_quiz_details(user_id):
    """
    Trigger export job for user quiz details
    """
    current_user = get_jwt_identity()
    
    # Check if current user is admin or the requested user
    if current_user.get('role') != 'admin' and current_user.get('id') != user_id:
        return jsonify({"message": "Access forbidden"}), 403
    
    try:
        data = request.get_json()
        
        # Get query parameters for date filtering
        start_date_str = data.get('start_date')  # Format: YYYY-MM-DD
        end_date_str = data.get('end_date')      # Format: YYYY-MM-DD
        
        filters = {}
        
        if start_date_str:
            try:
                filters['start_date'] = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                filters['end_date'] = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
        
        # Submit Celery task
        from export_tasks import export_user_quiz_data
        task = export_user_quiz_data.delay(user_id, filters)
        
        return jsonify({
            'message': 'Export job submitted successfully',
            'task_id': task.id,
            'status': 'PENDING',
            'user_id': user_id,
            'filters': filters
        }), 202
        
    except Exception as e:
        return jsonify({'error': f'Error submitting export job: {str(e)}'}), 400

@export_bp.route('/export/admin/all-quiz-details', methods=['POST'])
@jwt_required()
def export_all_quiz_details():
    """
    Trigger export job for admin quiz details
    """
    current_user = get_jwt_identity()
    
    # Check if current user is admin
    if current_user.get('role') != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    
    try:
        data = request.get_json()
        
        # Get query parameters for filtering
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        subject_id = data.get('subject_id')
        user_id = data.get('user_id')
        
        filters = {}
        
        if start_date_str:
            try:
                filters['start_date'] = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                filters['end_date'] = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
        
        if subject_id:
            filters['subject_id'] = int(subject_id)
        
        if user_id:
            filters['user_id'] = int(user_id)
        
        # Submit Celery task
        from export_tasks import export_admin_quiz_data
        task = export_admin_quiz_data.delay(current_user.get('id'), filters)
        
        return jsonify({
            'message': 'Export job submitted successfully',
            'task_id': task.id,
            'status': 'PENDING',
            'filters': filters
        }), 202
        
    except Exception as e:
        return jsonify({'error': f'Error submitting export job: {str(e)}'}), 400

@export_bp.route('/export/task/<task_id>/status', methods=['GET'])
@jwt_required()
def get_task_status(task_id):
    """
    Get the status of an export task
    """
    try:
        from app import celery
        
        task = celery.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'task_id': task_id,
                'state': task.state,
                'status': 'Task is pending...'
            }
        elif task.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'state': task.state,
                'status': task.info.get('status', ''),
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1)
            }
        elif task.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'state': task.state,
                'result': task.result,
                'csv_content': task.result.get('csv_content') if task.result else None,
                'filename': task.result.get('filename') if task.result else None
            }
        else:
            response = {
                'task_id': task_id,
                'state': task.state,
                'error': str(task.info)
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Error getting task status: {str(e)}'}), 400

 