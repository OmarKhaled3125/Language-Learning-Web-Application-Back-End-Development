from typing import Dict, Any, Tuple
from flask import request
from werkzeug.exceptions import BadRequest
from app.controllers.api.base_controller import BaseController
from app.services.question_service import QuestionService
from app.utils.file_upload import validate_file_upload
from app.utils.auth_decorators import token_required, admin_required



class QuestionController(BaseController):
    """Controller for handling question-related operations."""
    
    def __init__(self):
        """Initialize the question controller."""
        super().__init__('question', __name__)
        self.service = QuestionService()
        self._register_routes()
    
    def _register_routes(self) -> None:
        """Register all routes for the question controller."""
        # Register routes with strict_slashes=False to handle both with and without trailing slash
        self.blueprint.route('', methods=['GET'], strict_slashes=False)(token_required(self.get_questions))
        self.blueprint.route('/<int:question_id>', methods=['GET'], strict_slashes=False)(token_required(self.get_question))
        self.blueprint.route('', methods=['POST'], strict_slashes=False)(admin_required(self.create_question))
        self.blueprint.route('/<int:question_id>', methods=['PUT'], strict_slashes=False)(admin_required(self.update_question))
        self.blueprint.route('/<int:question_id>', methods=['DELETE'], strict_slashes=False)(admin_required(self.delete_question))
        self.blueprint.route('/<int:question_id>/choices', methods=['POST'], strict_slashes=False)(admin_required(self.add_choices))
        self.blueprint.route('/<int:question_id>/choices/<int:choice_id>', methods=['DELETE'], strict_slashes=False)(admin_required(self.delete_choice))
        self.blueprint.route('/<int:question_id>/choices/<int:choice_id>', methods=['PUT'], strict_slashes=False)(admin_required(self.update_choice))
    
    def get_questions(self) -> Tuple[Dict[str, Any], int]:
        """ Get all questions or filter by section. """
        section_id = request.args.get('section_id', type=int)
        questions = self.service.get_questions_by_section(section_id) if section_id else self.service.get_all()
        return self.success_response(data=[question.to_dict() for question in questions])
    
    def get_question(self, question_id: int) -> Tuple[Dict[str, Any], int]:
        """ Get a specific question by ID. """
        question = self.service.get_by_id(question_id)
        if not question:
            return self.error_response("Question not found", status_code=404)
        return self.success_response(data=question.to_dict())
    
    def create_question(self) -> Tuple[Dict[str, Any], int]:
        """ Create a new question. """
        try:
            # Support both JSON and form-data
            if request.is_json:
                data = request.get_json()
                question_file = None
            else:
                data = request.form
                question_file = request.files.get('question_content')

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
            print("Error creating question:", e)
            return self.error_response("Failed to create question", status_code=500)
    
    def update_question(self, question_id: int) -> Tuple[Dict[str, Any], int]:
        """ Update an existing question."""
        try:
            # Support both JSON and form-data
            if request.is_json:
                data = request.get_json()
                question_file = None
            else:
                data = request.form
                question_file = request.files.get('question_content')

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
        """ Delete a question. """
        try:
            if self.service.delete_question(question_id):
                return self.success_response(message="Question deleted successfully")
            return self.error_response("Question not found", status_code=404)
        except Exception as e:
            return self.error_response("Failed to delete question", status_code=500)

    def add_choices(self, question_id: int):
        """
        Add choices to a question.
        """
        try:
            if request.is_json:
                data = request.get_json()
                files = None
            else:
                data = request.form.to_dict()
                files = request.files
            choice = self.service.add_single_choice(question_id, data, files)
            return self.success_response(data=choice.to_dict(), message="Choice added successfully")
        except BadRequest as e:
            return self.error_response(str(e))
        except Exception as e:
            return self.error_response("Failed to add choice", status_code=500)


    def delete_choice(self, question_id: int, choice_id: int):
        """
        Delete a specific choice from a question.
        """
        try:
            self.service.delete_choice(question_id, choice_id)
            return self.success_response(message="Choice deleted successfully")
        except BadRequest as e:
            return self.error_response(str(e))
        except Exception as e:
            return self.error_response("Failed to delete choice", status_code=500)

    def update_choice(self, question_id: int, choice_id: int):
        """
        Update a specific choice for a question.
        """
        try:
            if request.is_json:
                data = request.get_json()
                files = None
            else:
                data = request.form.to_dict()
                files = request.files
            choice = self.service.update_single_choice(question_id, choice_id, data, files)
            return self.success_response(data=choice.to_dict(), message="Choice updated successfully")
        except BadRequest as e:
            return self.error_response(str(e))
        except Exception as e:
            return self.error_response("Failed to update choice", status_code=500)



# Create blueprint instance
question_bp = QuestionController().blueprint 