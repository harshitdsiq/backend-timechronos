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

class TimesheetStatus(PyEnum):
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    RECALLED = 'recalled'

class UserStatus(PyEnum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(50))
    email_domain = db.Column(db.String(50), unique=True, nullable=False)
    contact_email = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20))
    address = db.Column(db.Text)
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# class Country(db.Model):
#     __tablename__ = 'country'
    
#     id = db.Column(db.Integer, primary_key=True),
#     name = db.Column(db.String(100)), 
#     nicename = db.Column(db.String(100)),
#     iso3 = db.Column(db.String(3)),
#     iso = db.Column(db.String(2)),
#     numcode = db.Column(db.Integer),
#     phonecode = db.Column(db.String(10))

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
    #status = db.Column(SQLAlchemyEnum(UserStatus), default=UserStatus.ACTIVE,nullable=True)



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




class Timesheet(db.Model):
    __tablename__ = 'timesheets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users1.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(TimesheetStatus), 
                     nullable=False, 
                     default=TimesheetStatus.DRAFT)
    submitted_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    rejected_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    recalled_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                         onupdate=datetime.utcnow, nullable=False)
    
    user = db.relationship('User', backref='timesheets')


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    permissions = db.Column(db.Text, nullable=True)  # Can be a JSON string or comma-separated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship('Company', backref=db.backref('roles', lazy=True))


class Country(db.Model):
    __tablename__ = 'country'
    name = db.Column(db.String(100), primary_key=True)
    nicename = db.Column(db.String(100))
    iso3 = db.Column(db.String(3))
    iso = db.Column(db.String(2))
    numcode = db.Column(db.Integer)
    phonecode = db.Column(db.String(10))