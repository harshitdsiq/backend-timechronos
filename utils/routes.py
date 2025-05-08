from flask import Blueprint, request, jsonify
from .controllers import  register_company,register_user,login_user,register_client,login_client,create_project,create_task,create_timesheet,update_company_details
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .models import db, User
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,JWTManager

)

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

    access_token = create_access_token(identity={
        'user_id': response['user']['id'],
        'company_id': response['user']['company_id'],
        'role': response['user']['role']
    })

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": response['user']
    }), 200



#company registration
@auth_bp.route("/company-registration",methods=['POST'])
def companyLogin():
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

@auth_bp.route("/update-company/<int:company_id>", methods=['PUT'])
def update_company(company_id):
    data = request.get_json()
    return update_company_details(
        company_id=company_id,
        name=data.get('name'),
        email_domain=data.get('email_domain'),
        contact_email=data.get('contact_email'),
        contact_number=data.get('contact_number'),
        address=data.get('address')
    )


#client
@auth_bp.route('/client/register', methods=['POST'])
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



#projects
@auth_bp.route("/projects",methods=['POST'])
def create_new_project():
    data = request.get_json()
    response,status_code = create_project(data)
    return jsonify(response),status_code




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
