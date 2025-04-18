from flask import Blueprint, request, jsonify, render_template, current_app
from app.services.level_service import LevelService
from werkzeug.exceptions import BadRequest, NotFound, RequestEntityTooLarge
from werkzeug.utils import secure_filename
import os
import uuid
from app.extensions import db
from app.models.level import Level
from flask_jwt_extended import jwt_required
from http import HTTPStatus

level_bp = Blueprint('level', __name__, url_prefix='/api/levels')

# Ensure upload directory exists
def ensure_upload_dir():
    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'levels')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    return upload_dir

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file):
    if not file:
        raise BadRequest('No file provided')
    
    if file.filename == '':
        raise BadRequest('No selected file')
    
    if not allowed_file(file.filename):
        raise BadRequest('Invalid file type. Allowed types: ' + ', '.join(ALLOWED_EXTENSIONS))
    
    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_FILE_SIZE:
        raise RequestEntityTooLarge('File is too large. Maximum size is 5MB.')

# API Routes
@level_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_levels():
    try:
        levels = LevelService.get_all()
        return jsonify(levels), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve levels: ' + str(e)}), 500

@level_bp.route('/<int:level_id>', methods=['GET'])
@jwt_required()
def get_level(level_id):
    try:
        level = LevelService.get_by_id(level_id)
        if not level:
            raise NotFound(f'Level with ID {level_id} not found')
        return jsonify(level), 200
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve level {level_id}: {str(e)}'}), 500

@level_bp.route('/', methods=['POST'])
@jwt_required()
def create_level():
    try:
        # Handle image upload if present
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            validate_image(file)
            
            # Generate unique filename
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            new_filename = f"{uuid.uuid4()}.{ext}"
            
            # Save file
            upload_dir = ensure_upload_dir()
            file_path = os.path.join(upload_dir, new_filename)
            file.save(file_path)
            
            # Generate URL
            image_url = f'/static/uploads/levels/{new_filename}'
        
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description', '')
        
        if not name or not name.strip():
            raise BadRequest('Level name is required')
        
        # Create level
        level_data = {
            'name': name.strip(),
            'description': description.strip(),
            'image_url': image_url
        }
        
        level = LevelService.create(level_data)
        return jsonify(level), 201
    except (BadRequest, RequestEntityTooLarge) as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to create level: {str(e)}'}), 500

@level_bp.route('/<int:level_id>', methods=['PUT'])
@jwt_required()
def update_level(level_id):
    try:
        # Handle image upload if present
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            validate_image(file)
            
            # Generate unique filename
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            new_filename = f"{uuid.uuid4()}.{ext}"
            
            # Save file
            upload_dir = ensure_upload_dir()
            file_path = os.path.join(upload_dir, new_filename)
            file.save(file_path)
            
            # Generate URL
            image_url = f'/static/uploads/levels/{new_filename}'
        
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        
        # Update data
        update_data = {}
        if name is not None:
            if not name.strip():
                raise BadRequest('Level name cannot be empty')
            update_data['name'] = name.strip()
        if description is not None:
            update_data['description'] = description.strip()
        if image_url:
            update_data['image_url'] = image_url
        
        level = LevelService.update(level_id, update_data)
        if not level:
            raise NotFound(f'Level with ID {level_id} not found')
        return jsonify(level), 200
    except (BadRequest, NotFound) as e:
        return jsonify({'error': str(e)}), 404 if isinstance(e, NotFound) else 400
    except Exception as e:
        return jsonify({'error': f'Failed to update level {level_id}: {str(e)}'}), 500

@level_bp.route('/<int:level_id>', methods=['DELETE'])
@jwt_required()
def delete_level(level_id):
    try:
        result = LevelService.delete(level_id)
        if not result:
            raise NotFound(f'Level with ID {level_id} not found')
        return jsonify({'message': f'Level {level_id} deleted successfully'}), 200
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to delete level {level_id}: {str(e)}'}), 500 