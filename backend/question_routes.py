from flask import Blueprint, request, jsonify
from models import db
from models import Question
from flask_jwt_extended import jwt_required, get_jwt_identity

question_bp = Blueprint('question_bp', __name__)

@question_bp.route('/question', methods=['POST'])
@jwt_required()
def create_question():
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    data = request.get_json()

    question_statement = data.get('question_statement')
    quiz_id = data.get('quiz_id')
    option1 = data.get('option1')
    option2 = data.get('option2')
    option3 = data.get('option3')
    option4 = data.get('option4')
    correct_option = data.get('correct_option')

    if not question_statement or not quiz_id or not option1 or not option2 or not option3 or not option4 or not correct_option:
        return jsonify({'error': 'All fields are required'}), 400

    try:
        question = Question(
            question_statement=question_statement,
            quiz_id=quiz_id,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option
        )
        db.session.add(question)
        db.session.commit()
        return jsonify({'message': 'Question created', 'id': question.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@question_bp.route('/question/<int:question_id>', methods=['POST'])
@jwt_required()
def update_question(question_id):
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404

    data = request.get_json()
    try:
        question.question_statement = data.get('question_statement', question.question_statement)
        question.option1 = data.get('option1', question.option1)
        question.option2 = data.get('option2', question.option2)
        question.option3 = data.get('option3', question.option3)
        question.option4 = data.get('option4', question.option4)
        question.correct_option = data.get('correct_option', question.correct_option)

        db.session.commit()
        return jsonify({'message': 'Question updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@question_bp.route('/question/<int:question_id>', methods=['DELETE'])
@jwt_required()
def delete_question(question_id):
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    
    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404

        db.session.delete(question)
        db.session.commit()
        return jsonify({'message': 'Question deleted'}), 200
    except:
        return jsonify({'error': 'Error deleting question'}), 400

@question_bp.route('/questions', methods=['GET'])
def get_all_questions():
    try:
        questions = Question.query.all()
        result = [
            {
                'id': q.id,
                'question_statement': q.question_statement,
                'quiz_id': q.quiz_id,
                'option1': q.option1,
                'option2': q.option2,
                'option3': q.option3,
                'option4': q.option4,
                'correct_option': q.correct_option
            } for q in questions
        ]
        return jsonify(result), 200
    except:
        return jsonify({'error': 'Error getting questions'}), 400

@question_bp.route('/quizzes/<int:quiz_id>/questions', methods=['GET'])
def get_questions_by_quiz(quiz_id):
    try:
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        result = [
            {
                'id': q.id,
                'question_statement': q.question_statement,
                'option1': q.option1,
                'option2': q.option2,
                'option3': q.option3,
                'option4': q.option4,
                'correct_option': q.correct_option
            } for q in questions
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
