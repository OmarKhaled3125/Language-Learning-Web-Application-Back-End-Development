from flask import Blueprint, request, jsonify

general_bp = Blueprint('general', __name__)

def create_crud_routes(endpoint):
    # Unique function for `GET` and `POST`
    def get_and_create():
        if request.method == 'GET':
            return jsonify({"message": f"Get all {endpoint}"}), 200
        elif request.method == 'POST':
            return jsonify({"message": f"Create {endpoint}"}), 201
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
            return jsonify({"message": f"Get {endpoint} with id {id}"}), 200
        elif request.method == 'PUT':
            return jsonify({"message": f"Edit {endpoint} with id {id}"}), 200
        elif request.method == 'DELETE':
            return jsonify({"message": f"Delete {endpoint} with id {id}"}), 200
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
    "permission", "progress", "quiz", "role", "rolePermission", "roleUser",
    "user", "userCompletesLessons", "userTakesQuizzes", "voiceRecognition"
]

# Register all CRUD routes
for route in ENDPOINTS:
    create_crud_routes(route)

# UPLOAD ENDPOINT
@general_bp.route('/upload', methods=['POST'])
def upload():
    return jsonify({"message": "File uploaded successfully"}), 201