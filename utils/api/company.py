# utils/routes/company_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from utils.schema.models import db, Company
from utils.controllers import register_company,update_company_details

from flask_jwt_extended import create_access_token

company_bp = Blueprint('company', __name__, url_prefix='/company')

# Company Registration
@company_bp.route("/register", methods=['POST'])
def company_register():
    data = request.get_json()
    return register_company(
        name=data.get('name'),
        industry=data.get('industry'),
        email_domain=data.get('email_domain'),
        contact_email=data.get('contact_email'),
        contact_number=data.get('contact_number'),
        password=data.get('password'),
        address=data.get('address')
    )

# Company Login
@company_bp.route("/login", methods=['POST'])
def company_login():
    data = request.get_json()
    contact_email = data.get('contact_email')
    password = data.get('password')

    if not contact_email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    company = Company.query.filter_by(contact_email=contact_email).first()
    if not company or not check_password_hash(company.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(company.id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "company_id": company.id
    }), 200

# Update Profile
@company_bp.route("/update/<int:company_id>", methods=['PUT'])
@jwt_required()
def update_company(company_id):
    current_company_id = get_jwt_identity()

    if str(current_company_id) != str(company_id):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    return update_company_details(
        company_id=company_id,
        name=data.get('name'),
        email_domain=data.get('email_domain'),
        contact_email=data.get('contact_email'),
        contact_number=data.get('contact_number'),
        address=data.get('address')
    )

# Get Company Info
@company_bp.route("/profile", methods=['GET'])
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
