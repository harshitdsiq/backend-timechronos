# utils/routes/user_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from utils.controllers import (
    register_user, login_user, update_user_logic, delete_user_logic
)
from utils.schema.models import User
from flask_jwt_extended import create_access_token, create_refresh_token

user_bp = Blueprint('user', __name__, url_prefix='/user')

# --- User Signup ---
@user_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    required_fields = ['first_name', 'last_name', 'email', 'password', 'company_id', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    return register_user(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        password=data['password'],
        company_id=data['company_id'],
        role=data['role'],
        phone=data.get('phone')
    )

# --- User Login ---
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password required"}), 400

    response, status_code = login_user(
        email=data['email'],
        password=data['password']
    )

    if status_code != 200:
        return jsonify(response), status_code

    user_data = response['user']
    identity = str(user_data['id'])

    additional_claims = {
        "company_id": user_data['company_id'],
        "role": user_data['role']
    }

    access_token = create_access_token(identity=identity, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=identity, additional_claims=additional_claims)

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user_data
    }), 200

# --- Get All Users in Company ---
@user_bp.route('/all', methods=['GET'])
@jwt_required()
def get_users():
    try:
        jwt_data = get_jwt()
        company_id = jwt_data.get('company_id')

        if not company_id:
            return jsonify({"error": "Company ID not found in token"}), 400

        users = User.query.filter_by(company_id=company_id).all()

        users_list = [{
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role.value,
            "company_id": user.company_id,
            "created_at": user.created_at.isoformat()
        } for user in users]

        return jsonify(users_list), 200

    except Exception as e:
        print(f"Error in get_users: {e}")
        return jsonify({"error": "Internal server error"}), 500

# --- Update User ---
@user_bp.route('/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    response, status = update_user_logic(user_id, data)
    return jsonify(response), status

# --- Delete User ---
@user_bp.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    response, status = delete_user_logic(user_id)
    return jsonify(response), status
