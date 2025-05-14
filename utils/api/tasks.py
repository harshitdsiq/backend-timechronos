# utils/routes/task_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.controllers import (
    create_task,
    get_task_by_id,
    update_task,
    delete_task
)

task_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

# Create Task
@task_bp.route('/', methods=['POST'])
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

# Get Task by ID
@task_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    return get_task_by_id(task_id)

# Update Task
@task_bp.route('/<int:task_id>', methods=['PUT'])
def update_task_route(task_id):
    data = request.get_json()
    return update_task(task_id, data)

# Delete Task
@task_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task_route(task_id):
    return delete_task(task_id)
