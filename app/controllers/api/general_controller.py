from flask import Blueprint, request, jsonify
from app.services.general_service import GeneralService

general_bp = Blueprint('general', __name__)

def create_crud_routes(endpoint):
    # Unique function for `GET` and `POST`
    def get_and_create():
        if request.method == 'GET':
            result = GeneralService.get_all(endpoint)
            return jsonify(result), 200
        elif request.method == 'POST':
            result = GeneralService.create(endpoint)
            return jsonify(result), 201
        else:
            return jsonify({"error": "Method Not Allowed"}), 405

    # Dynamically assign unique endpoint names
    general_bp.add_url_rule(
        f'/{endpoint}', 
        view_func=get_and_create, 
        methods=['GET', 'POST'], 
        endpoint=f'{endpoint}_list'
    )

    # Unique function for `GET`, `PUT`, and `DELETE` with ID
    def manage_by_id(id):
        if request.method == 'GET':
            result = GeneralService.get_by_id(endpoint, id)
            return jsonify(result), 200
        elif request.method == 'PUT':
            result = GeneralService.update_by_id(endpoint, id)
            return jsonify(result), 200
        elif request.method == 'DELETE':
            result = GeneralService.delete_by_id(endpoint, id)
            return jsonify(result), 200
        # Ensure that unsupported methods return a valid response
        return jsonify({"error": "Method not allowed"}), 405  # Return a 405 error for unsupported methods

    # Dynamically assign unique endpoint names for ID-based operations
    general_bp.add_url_rule(
        f'/{endpoint}/<int:id>', 
        view_func=manage_by_id, 
        methods=['GET', 'PUT', 'DELETE'], 
        endpoint=f'{endpoint}_detail'
    )

# Add routes for all specified endpoints
ENDPOINTS = [
    "level", "section", "question", "questionChoice"
]

# Register all CRUD routes
for route in ENDPOINTS:
    create_crud_routes(route)

# UPLOAD ENDPOINT
@general_bp.route('/upload', methods=['POST'])
def upload():
    result = GeneralService.upload_file()
    return jsonify(result), 201