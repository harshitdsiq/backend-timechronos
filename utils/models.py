from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLAlchemyEnum


db = SQLAlchemy()

class UserRole(PyEnum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    EMPLOYEE = 'employee'
    CONTRACTOR = 'contractor'


class ProjectStatus(PyEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"

    

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(50))
    email_domain = db.Column(db.String(50), unique=True, nullable=False)
    contact_email = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)



class User(db.Model):
    __tablename__ = 'users1'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(255))
    role = db.Column(SQLAlchemyEnum(UserRole), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    company = db.relationship('Company', backref='users')



class Client(db.Model):
    __tablename__ = 'clients1'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    company = db.relationship('Company', backref=db.backref('clients', lazy=True))


class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients1.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    default_billable = db.Column(db.Boolean, default=True)
    employee_rate = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(ProjectStatus), nullable=False, default=ProjectStatus.PLANNED)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    client = db.relationship('Client', backref='projects', lazy=True)


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    billable = db.Column(db.Boolean, default=True, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    project = db.relationship('Project', backref='tasks')