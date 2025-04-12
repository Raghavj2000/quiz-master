from flask import Blueprint, request, jsonify
from models import db
from models import Subject

subject_bp = Blueprint('subject_bp', __name__)

# Create Subject
@subject_bp.route('/subject', methods=['POST'])
def create_subject():
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
