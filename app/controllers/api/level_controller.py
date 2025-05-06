"""
Level controller module that handles level-related API endpoints.
"""
from typing import Dict, Any, Tuple
from flask import request
from werkzeug.exceptions import BadRequest, NotFound
import logging

from app.controllers.api.base_controller import BaseController
from app.services.level_service import LevelService
from app.utils.file_upload import validate_file_upload, FileUploadError

logger = logging.getLogger(__name__)

class LevelController(BaseController):
    """Controller for handling level-related operations."""
    
    def __init__(self):
        """Initialize the level controller."""
        super().__init__('level', __name__)
        self.service = LevelService()
        self._register_routes()
    
    def _register_routes(self) -> None:
        """Register all routes for the level controller."""
        # Register routes with and without trailing slash
        self.blueprint.route('', methods=['GET'], strict_slashes=False)(self.get_levels)
        self.blueprint.route('/', methods=['GET'], strict_slashes=False)(self.get_levels)
        self.blueprint.route('/<int:level_id>', methods=['GET'], strict_slashes=False)(self.get_level)
        self.blueprint.route('/<int:level_id>/', methods=['GET'], strict_slashes=False)(self.get_level)
        self.blueprint.route('', methods=['POST'], strict_slashes=False)(self.create_level)
        self.blueprint.route('/', methods=['POST'], strict_slashes=False)(self.create_level)
        self.blueprint.route('/<int:level_id>', methods=['PUT'], strict_slashes=False)(self.update_level)
        self.blueprint.route('/<int:level_id>/', methods=['PUT'], strict_slashes=False)(self.update_level)
        self.blueprint.route('/<int:level_id>', methods=['DELETE'], strict_slashes=False)(self.delete_level)
        self.blueprint.route('/<int:level_id>/', methods=['DELETE'], strict_slashes=False)(self.delete_level)
    
    def get_levels(self) -> Tuple[Dict[str, Any], int]:
        """
        Get all levels.
        
        Returns:
            Tuple containing response dict and status code
        """
        try:
            levels = self.service.get_all()
            return self.success_response(data=levels)
        except Exception as e:
            logger.error(f"Error getting levels: {str(e)}")
            return self.error_response("Failed to retrieve levels", status_code=500)
    
    def get_level(self, level_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Get a specific level by ID.
        
        Args:
            level_id: ID of the level to retrieve
            
        Returns:
            Tuple containing response dict and status code
        """
        try:
            level = self.service.get_by_id(level_id)
            if not level:
                return self.error_response("Level not found", status_code=404)
            return self.success_response(data=level)  # level is already a dict
        except Exception as e:
            logger.error(f"Error getting level {level_id}: {str(e)}")
            return self.error_response("Failed to retrieve level", status_code=500)
    
    def create_level(self) -> Tuple[Dict[str, Any], int]:
        """
        Create a new level.
        
        Returns:
            Tuple containing response dict and status code
        """
        try:
            data = self.get_request_data()
            if 'name' not in data:
                return self.error_response("Name is required", status_code=400)
            
            file = request.files.get('image')
            if file:
                try:
                    validate_file_upload(file)
                except (BadRequest, FileUploadError) as e:
                    return self.error_response(str(e), status_code=400)
            
            level = self.service.create_level(data, file)
            return self.success_response(
                data=level,
                message="Level created successfully",
                status_code=201
            )
        except BadRequest as e:
            logger.warning(f"Bad request while creating level: {str(e)}")
            return self.error_response(str(e))
        except Exception as e:
            logger.error(f"Error creating level: {str(e)}")
            return self.error_response("Failed to create level", status_code=500)
    
    def update_level(self, level_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Update an existing level.
        
        Args:
            level_id: ID of the level to update
            
        Returns:
            Tuple containing response dict and status code
        """
        try:
            data = self.get_request_data()
            file = request.files.get('image')
            
            if file:
                try:
                    validate_file_upload(file)
                except (BadRequest, FileUploadError) as e:
                    return self.error_response(str(e), status_code=400)
            
            level = self.service.update_level(level_id, data, file)
            if not level:
                return self.error_response("Level not found", status_code=404)
            
            return self.success_response(
                data=level,
                message="Level updated successfully"
            )
        except BadRequest as e:
            logger.warning(f"Bad request while updating level {level_id}: {str(e)}")
            return self.error_response(str(e))
        except Exception as e:
            logger.error(f"Error updating level {level_id}: {str(e)}")
            return self.error_response("Failed to update level", status_code=500)
    
    def delete_level(self, level_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Delete a level.
        
        Args:
            level_id: ID of the level to delete
            
        Returns:
            Tuple containing response dict and status code
        """
        try:
            if self.service.delete_level(level_id):
                logger.info(f"Successfully deleted level {level_id}")
                return self.success_response(message="Level deleted successfully")
            logger.warning(f"Level {level_id} not found for deletion")
            return self.error_response("Level not found", status_code=404)
        except Exception as e:
            logger.error(f"Error deleting level {level_id}: {str(e)}")
            return self.error_response(str(e), status_code=500)


# Create blueprint instance
level_bp = LevelController().blueprint 