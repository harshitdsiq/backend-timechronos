from flask import Blueprint, request, jsonify
from utils.schema.models import User, Company,TokenBlacklist
from datetime import datetime
from utils.schema.models import db
from utils.api.authentication.auth_helper import AccessTokens
from utils.api.authentication.auth_helper import passwordHelper, AccessTokens
from utils.controllers import login_user
from enum import Enum
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
# from itsdangerous import URLSafeTimedSerializer
# from flask_mail import Message
# from utils.mail import mail,app

login_bp = Blueprint('login', __name__, url_prefix='/authenticate')


@login_bp.route('/login', methods=['POST'])
def unified_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not passwordHelper.check_password(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Determine role
    role = user.role.name if hasattr(user.role, 'name') else user.role
    if isinstance(role, Enum):
        role = role.value

    identity = str(user.id)
    additional_claims = {
        "company_id": user.company_id,
        "role": role
    }

    access_token = AccessTokens.create_access_token(identity=identity, additional_claims=additional_claims)
    refresh_token = AccessTokens.create_refresh_token(identity=identity, additional_claims=additional_claims)

    response_data = {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "company_id": user.company_id,
            "role": role
        }
    }

    return jsonify(response_data), 200

@login_bp.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    try:
        # Get the current token's claims
        jti = get_jwt()["jti"]
        token_type = get_jwt()["type"]
        user_identity = get_jwt_identity()
        expires = datetime.fromtimestamp(get_jwt()["exp"])
        epoch_expires = get_jwt()["exp"]
        
        # Add token to blacklist
        blacklisted_token = TokenBlacklist(
            jti=jti,
            token_type=token_type,
            user_identity=str(user_identity),
            revoked=True,
            expires=expires,
            epoch_expires=epoch_expires,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(blacklisted_token)
        db.session.commit()
        
        return jsonify({"message": "Successfully logged out"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    

@login_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        # Debug prints
        print(f"Received - Old: {old_password}, New: {new_password}")
        print(f"DB Hash: {user.password}")
        print(f"Old Password Correct: {passwordHelper.check_password(user.password, old_password)}")

        # Validation
        if not all([old_password, new_password]):
            return jsonify({"error": "Both passwords are required"}), 400

        if not passwordHelper.check_password(user.password, old_password):
            return jsonify({"error": "Old password is incorrect"}), 401

        if old_password == new_password:
            return jsonify({
                "error": "New password cannot be same as old",
                "debug": {
                    "old_password_match": passwordHelper.check_password(user.password, old_password),
                    "new_password_similarity": old_password == new_password
                }
            }), 400

        # Update password
        user.password = passwordHelper.hash_password(new_password)
        db.session.commit()

        return jsonify({"message": "Password changed successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



# @login_bp.route('/request-password-reset', methods=['POST'])
# def request_password_reset():
#     data = request.get_json()
#     email = data.get('email')

#     if not email:
#         return jsonify({"error": "Email is required"}), 400

#     user = User.query.filter_by(email=email).first()
#     if user:
#         # Generate reset token (valid for 30 minutes)
#         serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
#         token = serializer.dumps(user.email, salt='password-reset-salt')
        
#         # Create reset link
#         reset_link = url_for('login.reset_with_token', token=token, _external=True)
        
#         # Send email
#         msg = Message(
#             subject="Password Reset Request",
#             recipients=[user.email],
#             body=f"""Hello {user.first_name},
            
# To reset your password, please click the following link:
# {reset_link}

# This link will expire in 30 minutes.

# If you didn't request this, please ignore this email.""",
#             sender=app.config['MAIL_DEFAULT_SENDER']
#         )
#         mail.send(msg)
    
#     # Always return success to prevent email enumeration
#     return jsonify({
#         "message": "If an account with this email exists, a reset link has been sent"
#     }), 200

# @login_bp.route('/reset-password/<token>', methods=['POST'])
# def reset_with_token(token):
#     try:
#         # Verify token
#         serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
#         email = serializer.loads(token, salt='password-reset-salt', max_age=1800)  # 30 minutes
        
#         data = request.get_json()
#         if not data or 'password' not in data:
#             return jsonify({"error": "New password is required"}), 400
            
#         user = User.query.filter_by(email=email).first()
#         if not user:
#             return jsonify({"error": "User not found"}), 404
            
#         # Update password
#         user.password = passwordHelper.hash_password(data['password'])
#         db.session.commit()
        
#         # Revoke all existing tokens for this user
#         tokens = TokenBlacklist.query.filter_by(user_identity=str(user.id)).all()
#         for token in tokens:
#             token.revoked = True
#         db.session.commit()
        
#         return jsonify({"message": "Password has been reset successfully"}), 200
        
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": "Invalid or expired reset token"}), 400