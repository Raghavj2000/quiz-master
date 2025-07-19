from flask import Blueprint, request, jsonify
from models import db, Score, Quiz, Chapter, Subject
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

summary_bp = Blueprint('summary_bp', __name__)

@summary_bp.route('/summary/user/<int:user_id>/subject-quizzes', methods=['GET'])
@jwt_required()
def get_user_subject_quiz_summary(user_id):
    """
    Get the number of quizzes taken for each subject by a specific user
    Returns: List of subjects with quiz counts
    """
    current_user = get_jwt_identity()
    
    try:
        # Query to get subject-wise quiz counts for the user
        # Join Score -> Quiz -> Chapter -> Subject to get all necessary information
        subject_summary = db.session.query(
            Subject.id.label('subject_id'),
            Subject.name.label('subject_name'),
            func.count(Score.id).label('quiz_count')
        ).join(
            Chapter, Subject.id == Chapter.subject_id
        ).join(
            Quiz, Chapter.id == Quiz.chapter_id
        ).join(
            Score, Quiz.id == Score.quiz_id
        ).filter(
            Score.user_id == user_id
        ).group_by(
            Subject.id, Subject.name
        ).all()
        
        # Format the results
        result = [
            {
                'subject_id': row.subject_id,
                'subject_name': row.subject_name,
                'quiz_count': row.quiz_count
            }
            for row in subject_summary
        ]
        
        return jsonify({
            'user_id': user_id,
            'subject_summary': result,
            'total_subjects_with_quizzes': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving summary: {str(e)}'}), 400

@summary_bp.route('/summary/user/<int:user_id>/monthly-quizzes', methods=['GET'])
@jwt_required()
def get_user_monthly_quiz_summary(user_id):
    """
    Get the number of quizzes taken for each month by a specific user
    Returns: List of months with quiz counts
    """
    current_user = get_jwt_identity()
    
    try:
        # Query to get monthly quiz counts for the user
        # Extract year and month from timestamp and count quizzes
        monthly_summary = db.session.query(
            func.strftime('%Y-%m', Score.timestamp).label('month'),
            func.count(Score.id).label('quiz_count')
        ).filter(
            Score.user_id == user_id
        ).group_by(
            func.strftime('%Y-%m', Score.timestamp)
        ).order_by(
            func.strftime('%Y-%m', Score.timestamp).desc()
        ).all()
        
        # Format the results
        result = [
            {
                'month': row.month,
                'quiz_count': row.quiz_count
            }
            for row in monthly_summary
        ]
        
        return jsonify({
            'user_id': user_id,
            'monthly_summary': result,
            'total_months_with_quizzes': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving monthly summary: {str(e)}'}), 400 