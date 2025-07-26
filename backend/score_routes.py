from flask import Blueprint, request, jsonify
from models import db, Score
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import redis
import json

score_bp = Blueprint('score_bp', __name__)

# Initialize Redis client for caching
redis_client = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)

# Test Redis connection
try:
    redis_client.ping()
    print("✅ Redis connection successful")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")

def get_cached_data(cache_key):
    """Get data from Redis cache"""
    try:
        cached_data = redis_client.get(cache_key)
        print(f"Cache lookup for key '{cache_key}': {'FOUND' if cached_data else 'NOT FOUND'}")
        if cached_data:
            return json.loads(cached_data)
        return None
    except Exception as e:
        print(f"Redis cache error: {e}")
        return None

def set_cached_data(cache_key, data, expire_seconds=300):  # 5 minutes cache
    """Set data in Redis cache"""
    try:
        redis_client.setex(cache_key, expire_seconds, json.dumps(data))
        print(f"Cache set for key '{cache_key}' with {expire_seconds}s expiry")
    except Exception as e:
        print(f"Redis cache error: {e}")

@score_bp.route('/score', methods=['POST'])
@jwt_required()
def create_score():
    current_user = get_jwt_identity()
    data = request.get_json()

    quiz_id = data.get('quiz_id')
    total_scored = data.get('total_scored')
    total_questions = data.get('total_questions')
    user_id = data.get('user_id')  # Optional, will use JWT if not provided

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

    # Create cache key
    cache_key = "all_scores_admin"
    
    try:
        # Try to get data from cache first
        cached_result = get_cached_data(cache_key)
        if cached_result:
            return jsonify({
                'scores': cached_result['scores'],
                'total_scores': cached_result['total_scores'],
                'cached': True,
                'cache_timestamp': cached_result.get('timestamp')
            }), 200
        
        # If not in cache, query the database
        scores = Score.query.all()
        result = [
            {
                'id': s.id,
                'quiz_id': s.quiz_id,
                'user_id': s.user_id,
                'total_scored': s.total_scored,
                'total_questions': s.total_questions,
                'timestamp': s.timestamp.isoformat() if s.timestamp else None
            } for s in scores
        ]
        
        # Cache the result for 5 minutes
        cache_data = {
            'scores': result,
            'total_scores': len(result),
            'timestamp': datetime.now().isoformat()
        }
        set_cached_data(cache_key, cache_data, 300)  # 5 minutes
        
        return jsonify({
            'scores': result,
            'total_scores': len(result),
            'cached': False,
            'cache_timestamp': cache_data['timestamp']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

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
                'timestamp': s.timestamp.isoformat() if s.timestamp else None
            } for s in scores
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@score_bp.route('/users/<int:user_id>/scores', methods=['GET'])
def get_scores_by_user(user_id):
    # Create cache key
    cache_key = f"user_scores:{user_id}"
    
    try:
        # Try to get data from cache first
        cached_result = get_cached_data(cache_key)
        if cached_result:
            return jsonify({
                'scores': cached_result['scores'],
                'total_scores': cached_result['total_scores'],
                'cached': True,
                'cache_timestamp': cached_result.get('timestamp')
            }), 200
        
        # If not in cache, query the database
        scores = Score.query.filter_by(user_id=user_id).all()
        result = [
            {
                'id': s.id,
                'quiz_id': s.quiz_id,
                'total_scored': s.total_scored,
                'total_questions': s.total_questions,
                'timestamp': s.timestamp.isoformat() if s.timestamp else None
            } for s in scores
        ]
        
        # Cache the result for 5 minutes
        cache_data = {
            'scores': result,
            'total_scores': len(result),
            'timestamp': datetime.now().isoformat()
        }
        set_cached_data(cache_key, cache_data, 300)  # 5 minutes
        
        return jsonify({
            'scores': result,
            'total_scores': len(result),
            'cached': False,
            'cache_timestamp': cache_data['timestamp']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@score_bp.route('/my-scores', methods=['GET'])
@jwt_required()
def get_my_scores():
    current_user = get_jwt_identity()
    
    # Create cache key
    cache_key = f"my_scores:{current_user['id']}"
    
    try:
        # Try to get data from cache first
        cached_result = get_cached_data(cache_key)
        if cached_result:
            return jsonify({
                'scores': cached_result['scores'],
                'total_scores': cached_result['total_scores'],
                'cached': True,
                'cache_timestamp': cached_result.get('timestamp')
            }), 200
        
        # If not in cache, query the database
        scores = Score.query.filter_by(user_id=current_user['id']).all()
        result = [
            {
                'id': s.id,
                'quiz_id': s.quiz_id,
                'total_scored': s.total_scored,
                'total_questions': s.total_questions,
                'timestamp': s.timestamp.isoformat() if s.timestamp else None
            } for s in scores
        ]
        
        # Cache the result for 5 minutes
        cache_data = {
            'scores': result,
            'total_scores': len(result),
            'timestamp': datetime.now().isoformat()
        }
        set_cached_data(cache_key, cache_data, 300)  # 5 minutes
        
        return jsonify({
            'scores': result,
            'total_scores': len(result),
            'cached': False,
            'cache_timestamp': cache_data['timestamp']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


