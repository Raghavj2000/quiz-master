from flask import Blueprint, request, jsonify
from models import db
from models import Chapter
from flask_jwt_extended import jwt_required, get_jwt_identity

chapter_bp = Blueprint('chapter_bp', __name__)

# Create Chapter
@chapter_bp.route('/chapter', methods=['POST'])
@jwt_required()
def create_chapter():
    token = request.headers.get("Authorization").split()[1]  # Get the actual token
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    subject_id = data.get('subject_id')

    try:
        if not name or not subject_id:
            return jsonify({'error': 'Name and subject_id are required'}), 400
        
        chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(chapter)
        db.session.commit()

        return jsonify({'message': 'Chapter created', 'id': chapter.id}), 201
    except:
        return jsonify({'error': 'Error creating a chapter'}), 400

# Edit Chapter
@chapter_bp.route('/chapter/<int:chapter_id>', methods=['POST'])
def update_chapter(chapter_id):
    token = request.headers.get("Authorization").split()[1]  # Get the actual token
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    data = request.get_json()
    try:
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return jsonify({'error': 'Chapter not found'}), 404

        chapter.name = data.get('name', chapter.name)
        chapter.description = data.get('description', chapter.description)
        db.session.commit()

        return jsonify({'message': 'Chapter updated'}), 200
    except:
        return jsonify({'message': 'Error in updating chapter'}), 400

# Delete Chapter
@chapter_bp.route('/chapter/<int:chapter_id>', methods=['DELETE'])
def delete_chapter(chapter_id):
    token = request.headers.get("Authorization").split()[1]  # Get the actual token
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    data = request.get_json()
    try:
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return jsonify({'error': 'Chapter not found'}), 404

        db.session.delete(chapter)
        db.session.commit()
        return jsonify({'message': 'Chapter deleted'}), 200
    except:
        return jsonify({'error': 'Error deleting chapter'}), 400


@chapter_bp.route('/chapters', methods=['GET'])
def get_all_chapters():
    try:
        chapters = Chapter.query.all()
        result = [
            {'id': c.id, 'name': c.name, 'description': c.description, 'subject_id': c.subject_id}
            for c in chapters
        ]
        return jsonify(result), 200
    except:
        return jsonify({'error': 'Error getting chapters'}), 400


@chapter_bp.route('/chapters/search', methods=['GET'])
def search_chapters():
    try:
        keyword = request.args.get('search', '')

        chapters = Chapter.query.filter(
            Chapter.name.ilike(f'%{keyword}%')
        ).all()

        result = [
            {'id': c.id, 'name': c.name, 'description': c.description, 'subject_id': c.subject_id}
            for c in chapters
        ]
        return jsonify(result), 200
    except:
        return jsonify({'error': 'Error searching chapters'}), 400
    
@chapter_bp.route('/subjects/<int:subject_id>/chapters', methods=['GET'])
def get_chapters_for_subject(subject_id):
    try:
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()

        result = [
            {
                'id': chapter.id,
                'name': chapter.name,
                'description': chapter.description,
                'subject_id': chapter.subject_id
            }
            for chapter in chapters
        ]

        return jsonify(result), 200
    except:
        return jsonify({'error': 'Error retrieving chapters for subject'}), 400
