from flask import Blueprint, request, jsonify
from models import db
from models import Subject
from flask_jwt_extended import jwt_required, get_jwt_identity

subject_bp = Blueprint('subject_bp', __name__)

# Create Subject
@subject_bp.route('/subject', methods=['POST'])
@jwt_required()
def create_subject():
    token = request.headers.get("Authorization").split()[1]  # Get the actual token
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    subject = Subject(name=name, description=description)
    db.session.add(subject)
    db.session.commit()

    return jsonify({'message': 'Subject created', 'id': subject.id}), 201

# Edit Subject
@subject_bp.route('/subject/<int:subject_id>', methods=['POST'])
def update_subject(subject_id):
    token = request.headers.get("Authorization").split()[1]  # Get the actual token
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    data = request.get_json()
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404

    subject.name = data.get('name', subject.name)
    subject.description = data.get('description', subject.description)
    db.session.commit()

    return jsonify({'message': 'Subject updated'}), 200

# Delete Subject
@subject_bp.route('/subject/<int:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404

    db.session.delete(subject)
    db.session.commit()
    return jsonify({'message': 'Subject deleted'}), 200


@subject_bp.route('/subjects', methods=['GET'])
def get_all_subjects():
    subjects = Subject.query.all()
    result = [
        {'id': s.id, 'name': s.name, 'description': s.description}
        for s in subjects
    ]
    return jsonify(result), 200


@subject_bp.route('/subjects/search', methods=['GET'])
def search_subjects():
    keyword = request.args.get('search', '')

    subjects = Subject.query.filter(
        Subject.name.ilike(f'%{keyword}%')
    ).all()

    result = [
        {'id': s.id, 'name': s.name, 'description': s.description}
        for s in subjects
    ]
    return jsonify(result), 200
