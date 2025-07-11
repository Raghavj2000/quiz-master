from flask import Blueprint, request, jsonify
from models import db, Score
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

score_bp = Blueprint('score_bp', __name__)

@score_bp.route('/score', methods=['POST'])
@jwt_required()
def create_score():
    current_user = get_jwt_identity()
    data = request.get_json()

    quiz_id = data.get('quiz_id')
    total_scored = data.get('total_scored')
    total_questions = data.get('total_questions')
    user_id = data.get('user_id')
      # Optional, will use JWT if not provided

    if not quiz_id or total_scored is None:
        return jsonify({'error': 'quiz_id and total_scored are required'}), 400

    # Use user_id from request body if provided, otherwise use from JWT
    final_user_id = user_id if user_id is not None else current_user.get('id')
    
    if not final_user_id:
        return jsonify({'error': 'User ID not found in token'}), 400

    try:
        score = Score(
            quiz_id=quiz_id,
            user_id=final_user_id,
            total_scored=total_scored,
            total_questions=total_questions,
            timestamp=datetime.utcnow()
        )
        db.session.add(score)
        db.session.commit()
        return jsonify({'message': 'Score created', 'id': score.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@score_bp.route('/score/<int:score_id>', methods=['POST'])
@jwt_required()
def update_score(score_id):
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    score = Score.query.get(score_id)
    if not score:
        return jsonify({'error': 'Score not found'}), 404

    data = request.get_json()
    try:
        score.total_scored = data.get('total_scored', score.total_scored)
        db.session.commit()
        return jsonify({'message': 'Score updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@score_bp.route('/score/<int:score_id>', methods=['DELETE'])
@jwt_required()
def delete_score(score_id):
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    
    try:
        score = Score.query.get(score_id)
        if not score:
            return jsonify({'error': 'Score not found'}), 404

        db.session.delete(score)
        db.session.commit()
        return jsonify({'message': 'Score deleted'}), 200
    except:
        return jsonify({'error': 'Error deleting score'}), 400

@score_bp.route('/scores', methods=['GET'])
@jwt_required()
def get_all_scores():
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403

    try:
        scores = Score.query.all()
        result = [
            {
                'id': s.id,
                'quiz_id': s.quiz_id,
                'user_id': s.user_id,
                'total_scored': s.total_scored,
                'total_questions': s.total_questions,
                'timestamp': s.timestamp
            } for s in scores
        ]
        return jsonify(result), 200
    except:
        return jsonify({'error': 'Error getting scores'}), 400

@score_bp.route('/quizzes/<int:quiz_id>/scores', methods=['GET'])
def get_scores_by_quiz(quiz_id):
    try:
        scores = Score.query.filter_by(quiz_id=quiz_id).all()
        result = [
            {
                'id': s.id,
                'user_id': s.user_id,
                'total_scored': s.total_scored,
                'total_questions': s.total_questions,
                'timestamp': s.timestamp
            } for s in scores
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@score_bp.route('/users/<int:user_id>/scores', methods=['GET'])
def get_scores_by_user(user_id):
    try:
        scores = Score.query.filter_by(user_id=user_id).all()
        result = [
            {
                'id': s.id,
                'quiz_id': s.quiz_id,
                'total_scored': s.total_scored,
                'total_questions': s.total_questions,
                'timestamp': s.timestamp
            } for s in scores
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@score_bp.route('/my-scores', methods=['GET'])
@jwt_required()
def get_my_scores():
    current_user = get_jwt_identity()
    try:
        scores = Score.query.filter_by(user_id=current_user['id']).all()
        result = [
            {
                'id': s.id,
                'quiz_id': s.quiz_id,
                'total_scored': s.total_scored,
                'total_questions': s.total_questions,
                'timestamp': s.timestamp
            } for s in scores
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


