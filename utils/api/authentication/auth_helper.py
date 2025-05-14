import bcrypt
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, get_jti
from flask import jsonify, Blueprint
from datetime import datetime, timedelta
from utils.schema.models import db, TokenBlacklist, User

auth_helper = Blueprint('auth_helper', __name__)

jwt = JWTManager()

class passwordHelper:
    @staticmethod
    def hash_password(password):
        try: 
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            return hashed_password.decode('utf-8')
        except Exception as e:
            return jsonify({'message': 'Error hashing password: ' + str(e)}), 500

    def check_password( password, hashed):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            return jsonify({'message': 'Error checking password: ' + str(e)}), 500

class AccessTokens:
    def create_access_token(self, user):
        access_token = create_access_token(identity=str(user.id))
        jti = get_jti(access_token)
        token = TokenBlacklist(
            jti=jti,
            token_type="access",
            user_identity=str(user.id),
            revoked=False,
            expires=datetime.utcnow() + timedelta(minutes=15)  # Adjust as needed
        )
        db.session.add(token)
        db.session.commit()
        return access_token

    def create_refresh_token(self, user):
        refresh_token = create_refresh_token(identity=str(user.id))
        jti = get_jti(refresh_token)
        token = TokenBlacklist(
            jti=jti,
            token_type="refresh",
            user_identity=str(user.id),
            revoked=False,
            expires=datetime.utcnow() + timedelta(days=7)  # Adjust as needed
        )
        db.session.add(token)
        db.session.commit()
        return refresh_token

    @staticmethod
    def revoke_token(jti):
        token = TokenBlacklist.query.filter_by(jti=jti).first()
        if token:
            token.revoked = True
            db.session.commit()

    @staticmethod
    def is_token_revoked(jwt_payload):
        jti = jwt_payload['jti']
        token = TokenBlacklist.query.filter_by(jti=jti).first()
        return token.revoked if token else True

@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
    # Fetch user details and include in claims
    user = User.query.get(identity)
    if user:
        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'accounts_id': user.accounts_id
        }
    return {}