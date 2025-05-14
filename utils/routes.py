from flask import Blueprint, request, jsonify,json
from .controllers import  register_company,register_user,login_user,register_client,login_client,create_project,create_task,create_timesheet,update_company_details,get_company_details,get_projects_by_client,update_client_logic,delete_client_logic,update_project_logic,delete_project_logic,get_task_by_id,update_task,delete_task,update_user_logic,delete_user_logic,get_all_clients
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .schema.models import db, User,Company
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,JWTManager,get_jwt,create_access_token, create_refresh_token

)
from datetime import timedelta
auth_bp = Blueprint('auth', __name__)


#user login and signup
# @auth_bp.route('/signup', methods=['POST'])
# def signup():
#     data = request.get_json()

#     required_fields = ['first_name', 'last_name', 'email', 'password', 'company_id', 'role']
#     if not all(field in data for field in required_fields):
#         return jsonify({"error": "Missing required fields"}), 400

#     return register_user(
#         first_name=data['first_name'],
#         last_name=data['last_name'],
#         email=data['email'],
#         password=data['password'],
#         company_id=data['company_id'],
#         role=data['role'],
#         phone=data.get('phone')
#     )


# @auth_bp.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()

#     if not data or not data.get('email') or not data.get('password'):
#         return jsonify({"error": "Email and password required"}), 400

#     response, status_code = login_user(
#         email=data['email'],
#         password=data['password']
#     )

#     if status_code != 200:
#         return jsonify(response), status_code

#     user_data = response['user']
#     identity = str(user_data['id'])

#     additional_claims = {
#         "company_id": user_data['company_id'],
#         "role": user_data['role']
#     }

#     access_token = create_access_token(identity=identity, additional_claims=additional_claims)
#     refresh_token = create_refresh_token(identity=identity, additional_claims=additional_claims)

#     return jsonify({
#         "message": "Login successful",
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "user": user_data
#     }), 200

# # @auth_bp.route('/whoami', methods=['GET'])
# # @jwt_required()
# # def whoami():
# #     claims = get_jwt()
# #     return jsonify({
# #         "company_id": claims["company_id"],
# #         "role": claims["role"]
# #     })

# @auth_bp.route('/users', methods=['GET'])
# @jwt_required()
# def get_users():
#     try:
#         jwt_data = get_jwt() 
#         print("JWT Data:", jwt_data)

#         company_id = jwt_data.get('company_id')
#         print(company_id)
#         if not company_id:
#             return jsonify({"error": "Company ID not found in token"}), 400

#         users = User.query.filter_by(company_id=company_id).all()

#         users_list = []
#         for user in users:
#             users_list.append({
#                 "id": user.id,
#                 "first_name": user.first_name,
#                 "last_name": user.last_name,
#                 "email": user.email,
#                 "phone": user.phone,
#                 "role": user.role.value,
#                 "company_id": user.company_id,
#                 "created_at": user.created_at.isoformat()
#             })

#         return jsonify(users_list), 200

#     except Exception as e:
#         print(f"Error in get_users: {e}")
#         return jsonify({"error": "Internal server error"}), 500

# @auth_bp.route('/user/update/<int:user_id>', methods=['PUT'])
# def update_user(user_id):
#     data = request.get_json()
#     response, status = update_user_logic(user_id, data)
#     return jsonify(response), status


# @auth_bp.route('/user/delete/<int:user_id>', methods=['DELETE'])
# def delete_user(user_id):
#     response, status = delete_user_logic(user_id)
#     return jsonify(response), status
# # @auth_bp.route("/update-user-profile/<int:id>",methods=['PUT'])
# # def updateProfile(id):
# #     data = request.get_json()
# #     return update_user_profile(
# #         first_name = data.get('first_name'),
# #         last_name = data.get('last_name'),
# #         email= data.get('email'),
# #     )


#company registration



#client



#projects




#tasks 





#timesheets
