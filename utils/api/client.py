# utils/routes/client_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from utils.controllers import (
    get_all_clients,
    register_client,
    login_client,
    update_client_logic,
    delete_client_logic,
    get_all_clients_by_id
)

client_bp = Blueprint('client', __name__, url_prefix='/client')

# Get all clients
@client_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_clients_route():
    response, status_code = get_all_clients()
    return jsonify(response), status_code

@client_bp.route('/<int:client_id>', methods=['GET'])
@jwt_required()
def get_client_by_id(client_id):
    response, status_code = get_all_clients_by_id(client_id)
    return jsonify(response), status_code

# Register new client
@client_bp.route('/add', methods=['POST'])
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

# Client login
@client_bp.route('/login', methods=['POST'])
def client_login():
    data = request.get_json()

    if not data or not data.get('code'):
        return jsonify({"error": "Code is required"}), 400

    response, status_code = login_client(code=data['code'])

    return jsonify(response), status_code

# Update client
@client_bp.route('/update/<int:client_id>', methods=['PUT'])
@jwt_required()
def update_client(client_id):
    data = request.get_json()
    response, status = update_client_logic(client_id, data)
    return jsonify(response), status

# Delete client
@client_bp.route('/delete/<int:client_id>', methods=['DELETE'])
@jwt_required()
def delete_client(client_id):
    response, status = delete_client_logic(client_id)
    return jsonify(response), status
