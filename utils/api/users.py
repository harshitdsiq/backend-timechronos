# utils/routes/user_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from utils.controllers import (
    register_user, login_user, update_user_logic, delete_user_logic
)
from utils.schema.models import User, TokenBlacklist, Company

from utils.schema.models import db
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import create_access_token, create_refresh_token
from utils.api.authentication.auth_helper import passwordHelper, AccessTokens
from datetime import datetime
user_bp = Blueprint('user', __name__, url_prefix='/user')

# --- User Signup ---
@user_bp.route('/add', methods=['POST'])
@jwt_required()
def signup():
    try:
        # Get JWT claims and validate token
        claims = get_jwt()
        if AccessTokens.is_token_revoked(claims):
            return jsonify({'message': 'Token revoked, please login again'}), 401

        # Get and validate request data
        data = request.get_json()
        required_fields = ['first_name', 'last_name', 'email', 'password', 'role']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Verify company (either from JWT or request)
        company_id = claims.get('company_id') or data.get('company_id')
        if not company_id:
            return jsonify({"error": "Company ID required"}), 400

        # Check for existing user
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already exists"}), 400

        # Verify company exists
        if not Company.query.get(company_id):
            return jsonify({"error": "Company not found"}), 404

        # Prepare user data with audit info
        user_data = {
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'email': data['email'],
            'password': passwordHelper.hash_password(data['password']),
            'company_id': company_id,
            'role': data['role'],
            'phone': data.get('phone'),
        }

        # Create and save user
        new_user = User(**user_data)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "message": "User created successfully",
            "user": {
                "id": new_user.id,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "email": new_user.email,
                "company_id": new_user.company_id,
                "role": new_user.role.value if hasattr(new_user.role, 'value') else new_user.role,
                "created_at": datetime.utcnow().isoformat()
            }
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Unexpected error", "details": str(e)}), 500

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

    access_token = AccessTokens.create_access_token(identity=identity, additional_claims=additional_claims)
    print(f"Access Token: {access_token}")
    refresh_token = AccessTokens.create_refresh_token(identity=identity, additional_claims=additional_claims)

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
@jwt_required()
def update_user(user_id):
    try:
        # Get JWT claims and validate token
        claims = get_jwt()
        if AccessTokens.is_token_revoked(claims):
            return jsonify({'message': 'Token revoked, please login again'}), 401

        # Get request data
        data = request.get_json()
        
        # Verify the user exists and belongs to same company
        user = User.query.filter_by(id=user_id, company_id=claims.get('company_id')).first()
        if not user:
            return jsonify({"error": "User not found or unauthorized"}), 404

        # Prepare update data with audit info
        update_data = {
            **data,
            'id': user_id,
            'updated_by': f"{claims.get('first_name', '')} {claims.get('last_name', '')}".strip(),
            'updated_by_id': claims.get('id'),
            'accounts_id': claims.get('accounts_id')
        }

        # Handle password separately if present
        if 'password' in data:
            update_data['password'] = passwordHelper.hash_password(data['password'])

        # Apply updates
        if "first_name" in data:
            user.first_name = data["first_name"]
        if "last_name" in data:
            user.last_name = data["last_name"]
        if "email" in data:
            user.email = data["email"]
        if "phone" in data:
            user.phone = data["phone"]
        if "role" in data:
            user.role = data["role"]
        if "password" in data:
            user.password = update_data['password']

        db.session.commit()

        return jsonify({
            "message": "User updated successfully",
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "role": user.role.name if hasattr(user.role, 'name') else user.role,
                "company_id": user.company_id,
                "updated_by": update_data['updated_by'],
                "updated_at": datetime.utcnow().isoformat()
            }
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

# --- Delete User ---
@user_bp.route('/delete/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        claims = get_jwt()
        
        if AccessTokens.is_token_revoked(claims):
            return jsonify({'message': 'Token revoked, please login again'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        if claims.get('company_id') != user.company_id:
            return jsonify({"error": "Unauthorized to delete this user"}), 403
        
        tokens = TokenBlacklist.query.filter_by(user_identity=str(user.id)).all()
        for token in tokens:
            token.revoked = True
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            "message": "User deleted and all tokens revoked successfully",
            "deleted_user_id": user_id
        }), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500



@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        # Debug: Print token contents
        jwt_data = get_jwt()
        print("JWT DATA:", jwt_data)
        
        # Get user by ID only
        user = User.query.get(user_id)
        print("User found:", user)

        if not user:
            return jsonify({
                "error": "User not found",
                "user_id": user_id
            }), 404

        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "company_id": user.company_id,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }

        return jsonify(user_data), 200

    except Exception as e:
        print(f"Error in get_user: {e}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500
    



































#     from flask import request, jsonify, current_app, url_for
# from itsdangerous import URLSafeTimedSerializer
# from flask_mail import Message
# from utils.mail import mail
# from utils.schema.models import User
# from utils.authentication.auth_helper import passwordHelper
# from utils.apis.helper import Helper
# @authentication.route('/reset-password', methods=['POST'])
# def reset_password():
#     data = Helper(User).responseObject(request)
#     if not data or 'email' not in data:
#         return jsonify({'message': 'Email is required'}), 400
#     user = Helper(User).getRecordBy(email=data['email'])
#     if user:
#         token = URLSafeTimedSerializer(current_app.config['SECRET_KEY']).dumps(user.email, salt='password-reset-salt')
#         reset_link = url_for('authentication.reset_with_token', token=token, _external=True)
#         msg = Message(
#             subject="Password Reset Request",
#             recipients=[user.email],
#             body=f"Hi {user.name},\n\nReset your password using the link below (valid for 30 mins):\n{reset_link}",
#             sender=current_app.config['MAIL_DEFAULT_SENDER']
#         )
#         mail.send(msg)
#     return jsonify({'message': 'If the email exists, a reset link has been sent.'}), 200
# @authentication.route('/reset-password/<token>', methods=['POST'])
# def reset_with_token(token):
#     try:
#         email = URLSafeTimedSerializer(current_app.config['SECRET_KEY']).loads(token, salt='password-reset-salt', max_age=1800)
#     except Exception:
#         return jsonify({'message': 'Invalid or expired reset link.'}), 400
#     data = request.get_json()
#     if not data or 'password' not in data:
#         return jsonify({'message': 'Password is required.'}), 400
#     user = Helper(User).getRecordBy(email=email)
#     if not user:
#         return jsonify({'message': 'User not found.'}), 404
#     user.password = passwordHelper().hash_password(data['password'])
#     user.save()
#     return jsonify({'message': 'Password has been reset successfully.'}), 200