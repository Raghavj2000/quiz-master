from flask import Blueprint, request, jsonify
from models import db
from models import Quiz
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity


quiz_bp = Blueprint('quiz_bp', __name__)

@quiz_bp.route('/quiz', methods=['POST'])
@jwt_required()
def create_quiz():
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    data = request.get_json()

    name = data.get('name')
    chapter_id = data.get('chapter_id')
    date_of_quiz = data.get('date_of_quiz')
    time_duration = data.get('time_duration')
    remarks = data.get('remarks')

    if not chapter_id or not name:
        return jsonify({'error': 'chapter_id and name are required'}), 400

    try:
        quiz = Quiz(
            name=name,
            chapter_id=chapter_id,
            date_of_quiz=datetime.strptime(date_of_quiz, '%Y-%m-%d').date() if date_of_quiz else None,
            time_duration=(datetime.min + timedelta(minutes=time_duration)).time() if time_duration else None,
            remarks=remarks
        )
        db.session.add(quiz)
        db.session.commit()
        return jsonify({'message': 'Quiz created', 'id': quiz.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@quiz_bp.route('/quiz/<int:quiz_id>', methods=['POST'])
def update_quiz(quiz_id):
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404

    data = request.get_json()
    try:
        quiz.chapter_id = data.get('chapter_id', quiz.chapter_id)
        quiz.date_of_quiz = data.get('date_of_quiz', quiz.date_of_quiz)
        quiz.time_duration = data.get('time_duration', quiz.time_duration)
        quiz.remarks = data.get('remarks', quiz.remarks)

        db.session.commit()
        return jsonify({'message': 'Quiz updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@quiz_bp.route('/quiz/<int:quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404

        db.session.delete(quiz)
        db.session.commit()
        return jsonify({'message': 'Quiz deleted'}), 200
    except:
        return jsonify({'error': 'Error deleting quiz'}), 400


@quiz_bp.route('/quizzes', methods=['GET'])
def get_all_quizzes():
    try:
        quizzes = Quiz.query.all()
        result = [
            {
                'name': q.name,
                'id': q.id,
                'chapter_id': q.chapter_id,
                'chapter_name': q.chapter.name,  # Added chapter name
                'date_of_quiz': q.date_of_quiz,
                'time_duration': (q.time_duration.hour * 60 + q.time_duration.minute) if q.time_duration else None,
                'remarks': q.remarks,
                'questions': [
                    {'id': qu.quiz_id, 'name': qu.question_statement} for qu in q.questions
                ]
            } for q in quizzes
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@quiz_bp.route('/chapters/<int:chapter_id>/quizzes', methods=['GET'])
def get_quizzes_by_chapter(chapter_id):
    try:
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        result = [
            {
                'name': q.name,
                'id': q.id,
                'date_of_quiz': q.date_of_quiz,
                'time_duration': (q.time_duration.hour * 60 + q.time_duration.minute) if q.time_duration else None,
                'remarks': q.remarks
            } for q in quizzes
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

