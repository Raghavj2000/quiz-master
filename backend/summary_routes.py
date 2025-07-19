from flask import Blueprint, request, jsonify
from models import db, Score, Quiz, Chapter, Subject, User
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
        # Query to get monthly quiz counts for the user using raw SQL for better date handling
        monthly_summary = db.session.execute(
            db.text("""
                SELECT 
                    strftime('%Y-%m', timestamp) as month,
                    COUNT(*) as quiz_count
                FROM score 
                WHERE user_id = :user_id
                GROUP BY strftime('%Y-%m', timestamp)
                ORDER BY month DESC
            """),
            {'user_id': user_id}
        ).fetchall()
        
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

@summary_bp.route('/summary/admin/subject-top-scores', methods=['GET'])
@jwt_required()
def get_subject_top_scores():
    """
    Get the top scores for each subject (Admin only)
    Returns: List of subjects with top scores and user details
    """
    current_user = get_jwt_identity()
    
    # Check if current user is admin
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    
    try:
        # Query to get top scores for each subject
        # Join all necessary tables and get the highest score per subject
        top_scores = db.session.query(
            Subject.id.label('subject_id'),
            Subject.name.label('subject_name'),
            User.id.label('user_id'),
            User.username.label('username'),
            User.full_name.label('full_name'),
            func.max(Score.total_scored).label('top_score'),
            func.max(Score.total_questions).label('total_questions'),
            func.round(func.cast(func.max(Score.total_scored) * 100.0 / func.max(Score.total_questions), db.Float), 2).label('percentage')
        ).join(
            Chapter, Subject.id == Chapter.subject_id
        ).join(
            Quiz, Chapter.id == Quiz.chapter_id
        ).join(
            Score, Quiz.id == Score.quiz_id
        ).join(
            User, Score.user_id == User.id
        ).group_by(
            Subject.id, Subject.name, User.id, User.username, User.full_name
        ).subquery()
        
        # Get the highest score for each subject
        final_result = db.session.query(
            top_scores.c.subject_id,
            top_scores.c.subject_name,
            top_scores.c.user_id,
            top_scores.c.username,
            top_scores.c.full_name,
            top_scores.c.top_score,
            top_scores.c.total_questions,
            top_scores.c.percentage
        ).from_statement(
            db.text("""
                SELECT 
                    subject_id,
                    subject_name,
                    user_id,
                    username,
                    full_name,
                    top_score,
                    total_questions,
                    percentage
                FROM (
                    SELECT 
                        s.id as subject_id,
                        s.name as subject_name,
                        u.id as user_id,
                        u.username,
                        u.full_name,
                        sc.total_scored as top_score,
                        sc.total_questions,
                        ROUND(CAST(sc.total_scored * 100.0 / sc.total_questions AS FLOAT), 2) as percentage,
                        ROW_NUMBER() OVER (PARTITION BY s.id ORDER BY sc.total_scored DESC, sc.total_scored * 100.0 / sc.total_questions DESC) as rn
                    FROM subject s
                    JOIN chapter c ON s.id = c.subject_id
                    JOIN quiz q ON c.id = q.chapter_id
                    JOIN score sc ON q.id = sc.quiz_id
                    JOIN user u ON sc.user_id = u.id
                ) ranked
                WHERE rn = 1
                ORDER BY subject_name
            """)
        ).all()
        
        # Format the results
        result = [
            {
                'subject_id': row.subject_id,
                'subject_name': row.subject_name,
                'user_id': row.user_id,
                'username': row.username,
                'full_name': row.full_name,
                'top_score': row.top_score,
                'total_questions': row.total_questions,
                'percentage': row.percentage
            }
            for row in final_result
        ]
        
        return jsonify({
            'subject_top_scores': result,
            'total_subjects': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving subject top scores: {str(e)}'}), 400

@summary_bp.route('/summary/admin/subject-user-attempts', methods=['GET'])
@jwt_required()
def get_subject_user_attempts():
    """
    Get the number of unique users who attempted quizzes for each subject (Admin only)
    Returns: List of subjects with user attempt counts
    """
    current_user = get_jwt_identity()
    
    # Check if current user is admin
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    
    try:
        # Query to get unique user counts for each subject
        subject_user_counts = db.session.query(
            Subject.id.label('subject_id'),
            Subject.name.label('subject_name'),
            func.count(func.distinct(Score.user_id)).label('unique_users')
        ).join(
            Chapter, Subject.id == Chapter.subject_id
        ).join(
            Quiz, Chapter.id == Quiz.chapter_id
        ).join(
            Score, Quiz.id == Score.quiz_id
        ).group_by(
            Subject.id, Subject.name
        ).order_by(
            Subject.name
        ).all()
        
        # Format the results
        result = [
            {
                'subject_id': row.subject_id,
                'subject_name': row.subject_name,
                'unique_users': row.unique_users
            }
            for row in subject_user_counts
        ]
        
        return jsonify({
            'subject_user_attempts': result,
            'total_subjects': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error retrieving subject user attempts: {str(e)}'}), 400 