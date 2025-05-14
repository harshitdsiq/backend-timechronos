from flask import Blueprint, request, jsonify,json
from .controllers import  register_company,register_user,login_user,register_client,login_client,create_project,create_task,create_timesheet,update_company_details,get_company_details,get_projects_by_client,update_client_logic,delete_client_logic,update_project_logic,delete_project_logic,get_task_by_id,update_task,delete_task,update_user_logic,delete_user_logic,get_all_clients
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .models import db, User,Company
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,JWTManager,get_jwt,create_access_token, create_refresh_token

)
from datetime import timedelta
auth_bp = Blueprint('auth', __name__)


#user login and signup
@auth_bp.route('/signup', methods=['POST'])
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


@auth_bp.route('/login', methods=['POST'])
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

# @auth_bp.route('/whoami', methods=['GET'])
# @jwt_required()
# def whoami():
#     claims = get_jwt()
#     return jsonify({
#         "company_id": claims["company_id"],
#         "role": claims["role"]
#     })

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        jwt_data = get_jwt() 
        print("JWT Data:", jwt_data)

        company_id = jwt_data.get('company_id')
        print(company_id)
        if not company_id:
            return jsonify({"error": "Company ID not found in token"}), 400

        users = User.query.filter_by(company_id=company_id).all()

        users_list = []
        for user in users:
            users_list.append({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "role": user.role.value,
                "company_id": user.company_id,
                "created_at": user.created_at.isoformat()
            })

        return jsonify(users_list), 200

    except Exception as e:
        print(f"Error in get_users: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/user/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    response, status = update_user_logic(user_id, data)
    return jsonify(response), status


@auth_bp.route('/user/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    response, status = delete_user_logic(user_id)
    return jsonify(response), status
# @auth_bp.route("/update-user-profile/<int:id>",methods=['PUT'])
# def updateProfile(id):
#     data = request.get_json()
#     return update_user_profile(
#         first_name = data.get('first_name'),
#         last_name = data.get('last_name'),
#         email= data.get('email'),
#     )


#company registration
@auth_bp.route("/company-registration",methods=['POST'])
def companyRegister():
    data = request.get_json()
    return register_company(
        name=data.get('name'),
        industry=data.get('industry'),
        email_domain=data.get('email_domain'),
        contact_email=data.get('contact_email'),
        contact_number=data.get('contact_number'),
        password = data.get('password'),
        address=data.get('address')
    )

@auth_bp.route("/company-login", methods=['POST'])
def company_login():
    data = request.get_json()
    contact_email = data.get('contact_email')
    password = data.get('password')
    if not contact_email or not password:
        return jsonify({"error": "Email domain and password are required"}), 400

    company = Company.query.filter_by(contact_email=contact_email).first()
    if not company:
        return jsonify({"error": "Invalid email domain or password"}), 401

    if not check_password_hash(company.password, password):
        return jsonify({"error": "Invalid email domain or password"}), 401
    
    access_token = create_access_token(identity=str(company.id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "company_id": company.id
    }), 200

@auth_bp.route("/update-profile/<int:company_id>", methods=['PUT'])
# @jwt_required()
def update_company(company_id):
    # identity = json.loads(get_jwt_identity())   
    # if str(identity['company_id']) != str(company_id):
    #     return jsonify({"error": "Unauthorized"}), 403
    # current_identity = get_jwt_identity()
    
    # if str(current_identity['company_id']) != str(company_id):
    #     return jsonify({"error": "Unauthorized to update this company profile"}), 403
    data = request.get_json()
    return update_company_details(
        company_id=company_id,
        name=data.get('name'),
        email_domain=data.get('email_domain'),
        contact_email=data.get('contact_email'),
        contact_number=data.get('contact_number'),
        address=data.get('address')
    )

@auth_bp.route("/admin", methods=['GET'])
@jwt_required()
def get_company():
    company_id = get_jwt_identity()  
    
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"error": "Company not found"}), 404

    return jsonify({
        "company_id": company.id,
        "name": company.name,
        "email_domain": company.email_domain,
        "contact_email": company.contact_email,
        "contact_number": company.contact_number,
        "address": company.address
    }), 200


#client
@auth_bp.route('/client', methods=['GET'])
@jwt_required()
def get_all_clients_route():
    response, status_code = get_all_clients()
    return jsonify(response), status_code

@auth_bp.route('/client/add', methods=['POST'])
def client_register():
    data = request.get_json()

    if not data or not data.get('name') or not data.get('code') or not data.get('company_id'):
        return jsonify({"error": "Name, code, and company_id are required"}), 400

    response, status_code = register_client(
        name=data['name'],
        code=data['code'],
        company_id=data['company_id'],
        description=data.get('description', '')
    )

    return jsonify(response), status_code

@auth_bp.route('/client/login', methods=['POST'])
def client_login():
    data = request.get_json()

    if not data or not data.get('code'):
        return jsonify({"error": "Code is required"}), 400

    response, status_code = login_client(code=data['code'])

    return jsonify(response), status_code


@auth_bp.route('/client/update/<int:client_id>', methods=['PUT'])
@jwt_required()
def update_client(client_id):
    data = request.get_json()
    response, status = update_client_logic(client_id, data)
    return jsonify(response), status


@auth_bp.route('/client/delete/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    response, status = delete_client_logic(client_id)
    return jsonify(response), status


#projects
@auth_bp.route("/projects",methods=['POST'])
def create_new_project():
    data = request.get_json()
    response,status_code = create_project(data)
    return jsonify(response),status_code


@auth_bp.route("/active-projects/<int:client_id>",methods=['GET'])
def get_client_projects(client_id):
    return get_projects_by_client(client_id)


@auth_bp.route("/projects/<int:project_id>", methods=['PUT'])
def update_project(project_id):
    data = request.get_json()
    response, status_code = update_project_logic(project_id, data)
    return jsonify(response), status_code


@auth_bp.route("/projects/<int:project_id>", methods=['DELETE'])
def delete_project(project_id):
    response, status_code = delete_project_logic(project_id)
    return jsonify(response), status_code



#tasks 
@auth_bp.route("/tasks",methods=['POST'])
def register_task():
    data = request.get_json()

    required_fields = ['project_id', 'name', 'code', 'billable', 'start_date', 'end_date']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    response, status_code = create_task(
        project_id=data['project_id'],
        name=data['name'],
        code=data['code'],
        billable=data['billable'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        description=data.get('description', '')
    )
    return jsonify(response), status_code

@auth_bp.route('/task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    return get_task_by_id(task_id)

# --- Update Task ---
@auth_bp.route('/task/<int:task_id>', methods=['PUT'])
def update_task_route(task_id):
    data = request.get_json()
    return update_task(task_id, data)

# --- Delete Task ---
@auth_bp.route('/task/<int:task_id>', methods=['DELETE'])
def delete_task_route(task_id):
    return delete_task(task_id)




#timesheets
@auth_bp.route("/timesheets", methods=['POST'])
def create_timesheet_route():
    data = request.get_json()
    
    if not data or 'week_start' not in data or 'user_id' not in data:
        return jsonify({
            "error": "Both user_id and week_start are required",
            "example_request": {
                "user_id": 1,
                "week_start": "2023-06-12"
            }
        }), 400
        
    return create_timesheet(
        user_id=data['user_id'],  
        week_start=data['week_start']
    )
