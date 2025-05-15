# utils/routes/project_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.controllers import (
    create_project,
    get_projects_by_client,
    update_project_logic,
    delete_project_logic
)

project_bp = Blueprint('project', __name__, url_prefix='/projects')

# Create a new project
@project_bp.route('/', methods=['POST'])
@jwt_required()
def create_new_project():
    data = request.get_json()
    response, status_code = create_project(data)
    return jsonify(response), status_code

# Get all active projects for a specific client
@project_bp.route('/active/<int:client_id>', methods=['GET'])
@jwt_required()
def get_client_projects(client_id):
    return get_projects_by_client(client_id)

# Update a project
@project_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    data = request.get_json()
    response, status_code = update_project_logic(project_id, data)
    return jsonify(response), status_code

# Delete a project
@project_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    response, status_code = delete_project_logic(project_id)
    return jsonify(response), status_code
