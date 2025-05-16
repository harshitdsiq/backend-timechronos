from .schema.models import db, Company, User , Client, Project,Task,Timesheet,Role
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from enum import Enum 
from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from utils.api.authentication.auth_helper import passwordHelper
from utils.api.authentication.auth_helper import AccessTokens
from datetime import timedelta
from utils.schema.models import UserRole, ProjectStatus, TimesheetStatus



pwd_helper = passwordHelper()

def register_user(first_name, last_name, email, password, company_id, role, phone=None):
    try:
        if not all([first_name, last_name, email, password, company_id, role]):
            return {"error": "Missing required fields"}, 400

        if User.query.filter_by(email=email).first():
            return {"error": "Email already exists"}, 400

        if not Company.query.get(company_id):
            return {"error": "Company not found"}, 404
        
        # if role != 'ADMIN':
        #     return {"error":"only admins are allowed"}

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            role=role,
            company_id=company_id,
            password=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        return {"message": "User registered successfully", "user_id": new_user.id}, 201

    except IntegrityError as e:
        db.session.rollback()
        return {"error": "Database error", "details": str(e)}, 500

def login_user(email, password):
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return {"error": "Invalid credentials"}, 401

    return {
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role.value,
            "company_id": user.company_id
        }
    }, 200

def register_company(name, industry, email_domain, contact_email, 
                    contact_number,password, address=None): #code
    try:
        if Company.query.filter_by(email_domain=email_domain).first():
            return jsonify({
                "error": "A company with this domain is already registered. "
                         "Please contact your Company Administrator or support."
            }), 400

        new_company = Company(
            name=name,
            industry=industry,
            email_domain=email_domain.lower(),
            contact_email=contact_email,
            contact_number=contact_number,
            address=address,
            password = pwd_helper.hash_password(password),
            created_at=datetime.utcnow()
        )
        db.session.add(new_company)
        db.session.commit()
        

        admin_role = Role(
            company_id=new_company.id,
            name='Admin',
            description='Full administrative access',
            permissions='all',
            created_at=datetime.utcnow()
        )
        db.session.add(admin_role)
        db.session.flush()

        # admin_user = User(
        #     company_id=new_company.id,
        #     role_id=admin_role.id,
        #     first_name=contact_email.split('@')[0],
        #     email=contact_email,
        #     password_hash=generate_password_hash(password),
        #     role='admin',
        #     status='active',
        #     created_at=datetime.utcnow()
        # )
        admin_user = User(
        company_id=new_company.id,
        first_name=contact_email.split('@')[0],
        last_name="Admin",  # Required by model
        email=contact_email,
        password=passwordHelper.hash_password(password),
        role=UserRole.ADMIN,  
        #status='active',
        created_at=datetime.utcnow()
)
        db.session.add(admin_user)

        db.session.commit()

        return jsonify({
            "message": "Company registered successfully",
            "company_id": new_company.id,
            "admin_user": {
                "id": admin_user.id,
                "email": admin_user.email,
                "role": "admin"
            }
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        print(e)
        return jsonify({
            "error": "Database error occurred",
            "details": str(e)
        }), 500
    

def register_client(name, code, company_id, description):
    try:
        # Check for existing client with the same code
        existing_client = Client.query.filter_by(code=code).first()
        if existing_client:
            return {"error": "Client with this code already exists"}, 400

        # Create new client object
        new_client = Client(
            name=name,
            code=code,
            company_id=company_id,
            description=description
        )

        # Try adding to the database
        db.session.add(new_client)
        db.session.commit()

        return {
            "message": "Client registered successfully",
            "client": {
                "id": new_client.id,
                "name": new_client.name,
                "code": new_client.code,
                "company_id": new_client.company_id,
                "description": new_client.description
            }
        }, 201

    except IntegrityError:
        db.session.rollback()
        print(e)

        return {"error": "Integrity error: possible duplicate or foreign key violation"}, 500

    except SQLAlchemyError as e:
        db.session.rollback()
        print(e)
        
        return {"error": f"Database error: {str(e)}"}, 500

    except Exception as e:
        print(e)
        db.session.rollback()
        return {"error": f"Unexpected error: {str(e)}"}, 500
    


def login_client(code):
    client = Client.query.filter_by(code=code).first()

    if not client:
        return {"error": "Invalid code or client not found"}, 401

    identity = str(client.id)

    additional_claims = {
        "client_id": client.id,
        "company_id": client.company_id
    }

    access_token = create_access_token(
        identity=identity,
        additional_claims=additional_claims,
        expires_delta=timedelta(minutes=15)
    )
    refresh_token = create_refresh_token(
        identity=identity,
        additional_claims=additional_claims,
        expires_delta=timedelta(days=7)
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "client": {
            "id": client.id,
            "name": client.name,
            "code": client.code,
            "company_id": client.company_id,
            "description": client.description
        }
    }, 200


def create_project(data):
    if not data or not all(key in data for key in ('client_id', 'name', 'code', 'start_date', 'end_date', 'employee_rate')):
        return {"error": "Missing required fields"}, 400

    client = Client.query.filter_by(id=data['client_id']).first()
    if not client:
        return {"error": "Client not found"}, 404

    existing_project = Project.query.filter_by(code=data['code']).first()
    if existing_project:
        return {"error": "Project with this code already exists"}, 400

    new_project = Project(
        client_id=data['client_id'],
        name=data['name'],
        code=data['code'],
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d'),
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d'),
        default_billable=data.get('default_billable', True),
        employee_rate=data['employee_rate'],
        status=ProjectStatus[data['status'].upper()]  
    )

    try:
        db.session.add(new_project)
        db.session.commit()
        
        return {
            "message": "Project created successfully",
            "project": {
                "id": new_project.id,
                "name": new_project.name,
                "code": new_project.code,
                "client_id": new_project.client_id,
                "start_date": new_project.start_date,
                "end_date": new_project.end_date,
                "employee_rate": new_project.employee_rate,
                "status": new_project.status.name
            }
        }, 201
    except IntegrityError:
        db.session.rollback()
        return {"error": "Database error, possibly a conflict in data"}, 500
    

def create_task(project_id, name, code, billable, start_date, end_date, description):
    existing_task = Task.query.filter_by(code=code).first()
    if existing_task:
        return {"error": "Task with this code already exists"}, 400

    new_task = Task(
        project_id=project_id,
        name=name,
        code=code,
        billable=billable,
        start_date=start_date,
        end_date=end_date,
        description=description
    )

    try:
        db.session.add(new_task)
        db.session.commit()
        return {
            "message": "Task created successfully",
            "task": {
                "id": new_task.id,
                "project_id": new_task.project_id,
                "name": new_task.name,
                "code": new_task.code,
                "billable": new_task.billable,
                "start_date": new_task.start_date.isoformat(),
                "end_date": new_task.end_date.isoformat(),
                "description": new_task.description
            }
        }, 201
    except IntegrityError:
        db.session.rollback()
        return {"error": "Database error, possibly a conflict in data"}, 500


def create_timesheet(user_id, week_start):
    try:
        from .schema.models import User  
        if not User.query.get(user_id):
            return {"error": "User not found"}, 404

        
        week_start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
        
        if Timesheet.query.filter_by(user_id=user_id, week_start=week_start_date).first():
            return {"error": "Timesheet exists for this week"}, 409

        new_timesheet = Timesheet(
            user_id=user_id,
            week_start=week_start_date,
            status=TimesheetStatus.DRAFT
        )
        
        db.session.add(new_timesheet)
        db.session.commit()
        
        return {
            "message": "Timesheet created",
            "timesheet": {
                "id": new_timesheet.id,
                "user_id": new_timesheet.user_id,
                "week_start": new_timesheet.week_start.isoformat(),
                "status": new_timesheet.status.value
            }
        }, 201

    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}, 400
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500


def update_company_details(company_id, name, email_domain, contact_email, contact_number, address):
    try:
        company = Company.query.get(company_id)

        if not company:
            return jsonify({"error": "Company not found"}), 404

        if email_domain:
            existing = Company.query.filter(
                Company.email_domain == email_domain.lower(),
                Company.id != company_id
            ).first()
            if existing:
                return jsonify({"error": "Email domain already used by another company."}), 400
            company.email_domain = email_domain.lower()

        if name:
            company.name = name
        if contact_email:
            company.contact_email = contact_email
        if contact_number:
            company.contact_number = contact_number
        if address:
            company.address = address

        db.session.commit()

        return jsonify({
            "message": "Company details updated successfully",
            "company": {
                "id": company.id,
                "name": company.name,
                "email_domain": company.email_domain,
                "contact_email": company.contact_email,
                "contact_number": company.contact_number,
                "address": company.address
            }
        }), 200
                
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({
            "error": "Database error occurred",
            "details": str(e)
        }), 500
    


def get_company_details(company_id):
    company = Company.query.get(company_id)

    if not company:
        return jsonify({"error": "Company not found"}), 404

    return jsonify({
        "company": {
            "id": company.id,
            "name": company.name,
            "industry": company.industry,
            "email_domain": company.email_domain,
            "contact_email": company.contact_email,
            "contact_number": company.contact_number,
            "address": company.address,
            "created_at": company.created_at.isoformat()
        }
    }), 200
#def update_user_profile(first_name,last_name,email):
    
def get_projects_by_client(client_id):
    projects = Project.query.filter_by(client_id=client_id).all()
    
    if not projects:
        return jsonify({"message": "No projects found for this client."}), 404

    project_list = []
    for project in projects:
        project_list.append({
            "id": project.id,
            "name": project.name,
            "code": project.code,
            "start_date": project.start_date.isoformat(),
            "end_date": project.end_date.isoformat(),
            "default_billable": project.default_billable,
            "employee_rate": project.employee_rate,
            "status": project.status.name,
            "created_at": project.created_at.isoformat()
        })

    return jsonify(project_list), 200


def update_client_logic(client_id, data):
    client = Client.query.get(client_id)
    if not client:
        return {"error": "Client not found"}, 404

    try:
        if "name" in data:
            client.name = data["name"]
        if "description" in data:
            client.description = data["description"]
        
        db.session.commit()
        return {
            "message": "Client updated successfully",
            "client": {
                "id": client.id,
                "name": client.name,
                "code": client.code,
                "company_id": client.company_id,
                "description": client.description
            }
        }, 200
    except Exception as e:
        #print(e)
        db.session.rollback()
        return {"error": f"Update failed: {str(e)}"}, 500
    

def delete_client_logic(client_id):
    client = Client.query.get(client_id)
    if not client:
        return {"error": "Client not found"}, 404

    try:
        db.session.delete(client)
        db.session.commit()
        return {"message": "Client deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Delete failed: {str(e)}"}, 500



def update_project_logic(project_id, data):
    project = Project.query.get(project_id)
    if not project:
        return {"error": "Project not found"}, 404

    try:
        if 'name' in data:
            project.name = data['name']
        if 'code' in data:
            existing_project = Project.query.filter_by(code=data['code']).first()
            if existing_project and existing_project.id != project.id:
                return {"error": "Project code already exists"}, 400
        project.code = data['code']
        if 'start_date' in data:
            project.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in data:
            project.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        if 'default_billable' in data:
            project.default_billable = data['default_billable']
        if 'employee_rate' in data:
            project.employee_rate = float(data['employee_rate'])
        if 'status' in data:
            try:
                project.status = ProjectStatus[data['status'].upper()]
            except KeyError:
                return {"error": f"Invalid status '{data['status']}'"}, 400

        db.session.commit()

        return {
            "message": "Project updated successfully",
            "project": {
                "id": project.id,
                "name": project.name,
                "code": project.code,
                "start_date": project.start_date.isoformat(),
                "end_date": project.end_date.isoformat(),
                "default_billable": project.default_billable,
                "employee_rate": project.employee_rate,
                "status": project.status.name
            }
        }, 200

    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to update project: {str(e)}"}, 500

def delete_project_logic(project_id):
    project = Project.query.get(project_id)
    if not project:
        return {"error": "Project not found"}, 404

    try:
        Task.query.filter_by(project_id=project.id).delete()
        db.session.delete(project)
        db.session.commit()
        return {"message": "Project deleted successfully"}, 200

    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to delete project: {str(e)}"}, 500
    


def get_task_by_id(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {"error": "Task not found"}, 404

    return {
        "id": task.id,
        "project_id": task.project_id,
        "name": task.name,
        "code": task.code,
        "billable": task.billable,
        "start_date": task.start_date.isoformat(),
        "end_date": task.end_date.isoformat(),
        "description": task.description,
        "created_at": task.created_at.isoformat()
    }, 200


def update_task(task_id, data):
    task = Task.query.get(task_id)
    if not task:
        return {"error": "Task not found"}, 404

    try:
        task.name = data.get('name', task.name)
        task.code = data.get('code', task.code)
        task.billable = data.get('billable', task.billable)
        task.start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d') if data.get('start_date') else task.start_date
        task.end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d') if data.get('end_date') else task.end_date
        task.description = data.get('description', task.description)

        db.session.commit()

        return {"message": "Task updated successfully"}, 200

    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to update task: {str(e)}"}, 500


def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {"error": "Task not found"}, 404

    try:
        db.session.delete(task)
        db.session.commit()
        return {"message": "Task deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to delete task: {str(e)}"}, 500



def update_user_logic(user_id, data):
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    try:
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

        db.session.commit()

        return {
            "message": "User updated successfully",
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "role": user.role.name,
                "company_id": user.company_id
            }
        }, 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": f"Update failed: {str(e)}"}, 500


def delete_user_logic(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    try:
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully"}, 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": f"Delete failed: {str(e)}"}, 500
    



def get_all_clients():
    try:
        clients = Client.query.all()
        
        clients_data = [{
            "id": client.id,
            "name": client.name,
            "code": client.code,
            "company_id": client.company_id,
            "description": client.description,
            "status": client.status if hasattr(client, 'status') else 'Active', 
            "created_at": client.created_at.isoformat() if client.created_at else None
        } for client in clients]
        #print(clients_data)

        return {
            "message": "Clients retrieved successfully",
            "clients": clients_data,
            "count": len(clients_data)
        }, 200

    except SQLAlchemyError as e:
        print(e)
        return {"error": f"Database error: {str(e)}"}, 500

    except Exception as e:
        print(e)
        return {"error": f"Unexpected error: {str(e)}"}, 500
    
def get_all_clients_by_id(client_id):
    try:
        client = Client.query.get(client_id)
        if not client:
            return {"error": "Client not found"}, 404

        client_data = {
            "id": client.id,
            "name": client.name,
            "code": client.code,
            "company_id": client.company_id,
            "description": client.description,
            "status": client.status if hasattr(client, 'status') else 'Active', 
            "created_at": client.created_at.isoformat() if client.created_at else None
        }

        return {
            "message": "Client retrieved successfully",
            "client": client_data
        }, 200

    except SQLAlchemyError as e:
        print(e)
        return {"error": f"Database error: {str(e)}"}, 500

    except Exception as e:
        print(e)
        return {"error": f"Unexpected error: {str(e)}"}, 500
    
