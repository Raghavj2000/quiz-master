from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, decode_token
from models import db, User

api = Blueprint('api', __name__)

@api.route('/register', methods=['POST'])
def register():
    data = request.json
    print(data)
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "User already exists", "statusCode": "400"}), 400
    
    new_user = User(username=data['username'], 
                    role=data['role'],
                    full_name = data['full_name'],
                    qualification = data['qualification'],
                    dob = data['dob'])
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User created successfully", "statusCode": "200"}), 201

@api.route('/logi', methods = ['POST'])
def logi():
    print(request)
    data = request.json
    print(data)
    user = User.query.filter_by(username=data['username']).first()
    print(user)
    
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity={"username": user.username, "role": user.role})
        return jsonify(access_token=access_token, 
                       statusCode="200", 
                       username = user.username,
                       role=user.role,
                       full_name=user.full_name), 200
    
    return jsonify({"message": "Invalid credentials", "statusCode": "401"}), 401

@api.route('/admin', methods=['GET'])
@jwt_required()
def admin_only():
    token = request.headers.get("Authorization").split()[1]  # Get the actual token
    print(token)
    current_user = get_jwt_identity()
    print(current_user)
    
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    
    return jsonify({"message": f"Welcome Admin {current_user['username']}!"}), 200


@api.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    token = request.headers.get("Authorization").split()[1]  # Get the actual token
    current_user = get_jwt_identity()
    
    if current_user['role'] != 'admin':
        return jsonify({"message": "Access forbidden"}), 403
    
    users = User.query.all()
    result = [
        {'id': u.id, 'username': u.username, 'role': u.role, 'full_name': u.full_name, 'qualification': u.qualification, 'dob': u.dob}
        for u in users
    ]
    return jsonify(result), 200