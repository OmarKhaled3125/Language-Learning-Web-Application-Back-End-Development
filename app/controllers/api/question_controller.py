"""
Question controller module that handles question-related API endpoints.
"""
from typing import Dict, Any, Tuple
from flask import request
from werkzeug.exceptions import BadRequest

from app.controllers.api.base_controller import BaseController
from app.services.question_service import QuestionService
from app.utils.file_upload import validate_file_upload


class QuestionController(BaseController):
    """Controller for handling question-related operations."""
    
    def __init__(self):
        """Initialize the question controller."""
        super().__init__('question', __name__)
        self.service = QuestionService()
        self._register_routes()
    
    def _register_routes(self) -> None:
        """Register all routes for the question controller."""
        # Register routes with and without trailing slash
        self.blueprint.route('', methods=['GET'], strict_slashes=False)(self.get_questions)
        self.blueprint.route('/', methods=['GET'], strict_slashes=False)(self.get_questions)
        self.blueprint.route('/<int:question_id>', methods=['GET'], strict_slashes=False)(self.get_question)
        self.blueprint.route('/<int:question_id>/', methods=['GET'], strict_slashes=False)(self.get_question)
        self.blueprint.route('', methods=['POST'], strict_slashes=False)(self.create_question)
        self.blueprint.route('/', methods=['POST'], strict_slashes=False)(self.create_question)
        self.blueprint.route('/<int:question_id>', methods=['PUT'], strict_slashes=False)(self.update_question)
        self.blueprint.route('/<int:question_id>/', methods=['PUT'], strict_slashes=False)(self.update_question)
        self.blueprint.route('/<int:question_id>', methods=['DELETE'], strict_slashes=False)(self.delete_question)
        self.blueprint.route('/<int:question_id>/', methods=['DELETE'], strict_slashes=False)(self.delete_question)
    
    def get_questions(self) -> Tuple[Dict[str, Any], int]:
        """
        Get all questions or filter by section.
        
        Returns:
            Tuple containing response dict and status code
        """
        section_id = request.args.get('section_id', type=int)
        questions = self.service.get_questions_by_section(section_id) if section_id else self.service.get_all()
        return self.success_response(data=[question.to_dict() for question in questions])
    
    def get_question(self, question_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Get a specific question by ID.
        
        Args:
            question_id: ID of the question to retrieve
            
        Returns:
            Tuple containing response dict and status code
        """
        question = self.service.get_by_id(question_id)
        if not question:
            return self.error_response("Question not found", status_code=404)
        return self.success_response(data=question.to_dict())
    
    def create_question(self) -> Tuple[Dict[str, Any], int]:
        """
        Create a new question.
        
        Returns:
            Tuple containing response dict and status code
        """
        try:
            data = self.get_request_data()
            question_file = request.files.get('question_file')
            
            if question_file:
                validate_file_upload(question_file)
            
            question = self.service.create_question(data, question_file)
            return self.success_response(
                data=question.to_dict(),
                message="Question created successfully",
                status_code=201
            )
        except BadRequest as e:
            return self.error_response(str(e))
        except Exception as e:
            return self.error_response("Failed to create question", status_code=500)
    
    def update_question(self, question_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Update an existing question.
        
        Args:
            question_id: ID of the question to update
            
        Returns:
            Tuple containing response dict and status code
        """
        try:
            data = self.get_request_data()
            question_file = request.files.get('question_file')
            
            if question_file:
                validate_file_upload(question_file)
            
            question = self.service.update_question(question_id, data, question_file)
            if not question:
                return self.error_response("Question not found", status_code=404)
            
            return self.success_response(
                data=question.to_dict(),
                message="Question updated successfully"
            )
        except BadRequest as e:
            return self.error_response(str(e))
        except Exception as e:
            return self.error_response("Failed to update question", status_code=500)
    
    def delete_question(self, question_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Delete a question.
        
        Args:
            question_id: ID of the question to delete
            
        Returns:
            Tuple containing response dict and status code
        """
        try:
            if self.service.delete_question(question_id):
                return self.success_response(message="Question deleted successfully")
            return self.error_response("Question not found", status_code=404)
        except Exception as e:
            return self.error_response("Failed to delete question", status_code=500)


# Create blueprint instance
question_bp = QuestionController().blueprint 