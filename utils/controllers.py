from .models import db, Company, User , Client, Project,ProjectStatus,Task,Timesheet,TimesheetStatus
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy.exc import IntegrityError
from enum import Enum 
from flask import jsonify

def register_user(first_name, last_name, email, password, company_id, role, phone=None):
    try:
        if not all([first_name, last_name, email, password, company_id, role]):
            return {"error": "Missing required fields"}, 400

        if User.query.filter_by(email=email).first():
            return {"error": "Email already exists"}, 400

        if not Company.query.get(company_id):
            return {"error": "Company not found"}, 404

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
                    contact_number,password, address=None):
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
            password = generate_password_hash(password),
            created_at=datetime.utcnow()
        )
        db.session.add(new_company)
        db.session.commit()

        return jsonify({
            "message": "Company registered successfully",
            "company_id": new_company.id
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({
            "error": "Database error occurred",
            "details": str(e)
        }), 500
    

def register_client(name, code, company_id, description):
    client = Client.query.filter_by(code=code).first()
    if client:
        return {"error": "Client with this code already exists"}, 400

    new_client = Client(
        name=name,
        code=code,
        company_id=company_id,
        description=description
    )

    try:
        db.session.add(new_client)
        db.session.commit()
        return {"message": "Client registered successfully", "client": {
            "id": new_client.id,
            "name": new_client.name,
            "code": new_client.code,
            "company_id": new_client.company_id,
            "description": new_client.description
        }}, 201
    except IntegrityError:
        db.session.rollback()
        return {"error": "Database error, possibly a conflict in data"}, 500
    


def login_client(code):
    client = Client.query.filter_by(code=code).first()

    if not client:
        return {"error": "Invalid code or client not found"}, 401

    return {
        "message": "Login successful",
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
        status=ProjectStatus[data['status'].upper()]  # Ensure valid status enum
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
        from .models import User  
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
