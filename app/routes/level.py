from flask import Blueprint, request, jsonify, render_template, current_app
from app.services.level_service import LevelService
from werkzeug.exceptions import BadRequest, NotFound, RequestEntityTooLarge
from werkzeug.utils import secure_filename
import os
import uuid

level_bp = Blueprint('level', __name__)

# Ensure upload directory exists
def ensure_upload_dir():
    upload_dir = os.path.join(current_app.static_folder, 'uploads')
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
def get_all_levels():
    try:
        levels = LevelService.get_all()
        return jsonify(levels), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve levels: ' + str(e)}), 500

@level_bp.route('/<int:level_id>', methods=['GET'])
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
def create_level():
    try:
        data = request.get_json()
        if not data:
            raise BadRequest('No data provided')
        
        if 'name' not in data or not data['name'].strip():
            raise BadRequest('Level name is required')
        
        # Sanitize input
        data['name'] = data['name'].strip()
        if 'description' in data:
            data['description'] = data['description'].strip()
        if 'image' in data:
            data['image'] = data['image'].strip()
            if data['image'].startswith('data:'):
                raise BadRequest('Invalid image format. Please upload the image first.')
        
        level = LevelService.create(data)
        return jsonify(level), 201
    except BadRequest as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to create level: {str(e)}'}), 500

@level_bp.route('/<int:level_id>', methods=['PUT'])
def update_level(level_id):
    try:
        data = request.get_json()
        if not data:
            raise BadRequest('No data provided')
        
        if 'name' in data and not data['name'].strip():
            raise BadRequest('Level name cannot be empty')
        
        # Sanitize input
        if 'name' in data:
            data['name'] = data['name'].strip()
        if 'description' in data:
            data['description'] = data['description'].strip()
        if 'image' in data:
            data['image'] = data['image'].strip()
            if data['image'].startswith('data:'):
                raise BadRequest('Invalid image format. Please upload the image first.')
        
        level = LevelService.update(level_id, data)
        if not level:
            raise NotFound(f'Level with ID {level_id} not found')
        return jsonify(level), 200
    except (BadRequest, NotFound) as e:
        return jsonify({'error': str(e)}), 404 if isinstance(e, NotFound) else 400
    except Exception as e:
        return jsonify({'error': f'Failed to update level {level_id}: {str(e)}'}), 500

@level_bp.route('/<int:level_id>', methods=['DELETE'])
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

@level_bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'image' not in request.files:
            raise BadRequest('No image file provided')
        
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
        
        # Return URL
        return jsonify({
            'url': f'/static/uploads/levels/{new_filename}'
        }), 201
    except (BadRequest, RequestEntityTooLarge) as e:
        return jsonify({'error': str(e)}), 413 if isinstance(e, RequestEntityTooLarge) else 400
    except Exception as e:
        return jsonify({'error': f'Failed to upload image: {str(e)}'}), 500 