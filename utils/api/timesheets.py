# utils/routes/timesheet_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.controllers import create_timesheet

timesheet_bp = Blueprint('timesheets', __name__, url_prefix='/timesheets')

# Create Timesheet
@timesheet_bp.route('/', methods=['POST'])
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
