"""
Question service module that handles question-related business logic.
"""
from typing import List, Optional, Dict, Any
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest

from app.models.question import Question, QuestionChoice, QuestionType, AnswerType, ChoiceType
from app.services.base_service import BaseService
from app.utils.file_upload import save_file, delete_file
from app import db
from sqlalchemy.exc import SQLAlchemyError


class QuestionService(BaseService):
    """Service class for handling question-related operations."""
    
    def __init__(self):
        """Initialize the question service."""
        super().__init__(Question)
    
    def create_question(self, data: Dict[str, Any], question_file: Optional[FileStorage] = None) -> Question:
        """
        Create a new question with optional file upload.
        
        Args:
            data: Dictionary containing question data
            question_file: Optional file to upload for question content
            
        Returns:
            Question: Created question instance
            
        Raises:
            BadRequest: If required data is missing
        """
        if not data.get('section_id'):
            raise BadRequest("Section ID is required")
            
        if not data.get('question_type'):
            raise BadRequest("Question type is required")
            
        if not data.get('answer_type'):
            raise BadRequest("Answer type is required")
            
        # Handle question content file upload
        if question_file:
            file_path = save_file(question_file, 'questions')
            data['question_content'] = file_path
        elif not data.get('question_content'):
            raise BadRequest("Question content is required")
            
        # Create question
        question = Question(
            section_id=data['section_id'],
            question_type=QuestionType(data['question_type']),
            question_content=data['question_content'],
            answer_type=AnswerType(data['answer_type'])
        )
        
        # Handle answers based on answer type
        if data['answer_type'] == AnswerType.MULTIPLE_CHOICE.value:
            if not data.get('choices'):
                raise BadRequest("Choices are required for multiple choice questions")
                
            # Validate that at least one choice is marked as correct
            has_correct_choice = False
            for choice_data in data['choices']:
                if choice_data.get('is_correct'):
                    has_correct_choice = True
                choice = QuestionChoice(
                    choice_type=ChoiceType(choice_data['type']),
                    content=choice_data['content'],
                    is_correct=choice_data.get('is_correct', False)
                )
                question.choices.append(choice)
                
            if not has_correct_choice:
                raise BadRequest("At least one choice must be marked as correct")
        else:  # Fill in the blank
            if not data.get('correct_answer'):
                raise BadRequest("Correct answer is required for fill-in-the-blank questions")
            question.correct_answer = data['correct_answer']
        
        try:
            db.session.add(question)
            db.session.commit()
            return question
        except SQLAlchemyError as e:
            db.session.rollback()
            raise BadRequest(f"Database error: {str(e)}")
    
    def update_question(self, question_id: int, data: Dict[str, Any], question_file: Optional[FileStorage] = None) -> Optional[Question]:
        """
        Update an existing question with optional file upload.
        
        Args:
            question_id: ID of the question to update
            data: Dictionary containing updated question data
            question_file: Optional new file to upload
            
        Returns:
            Optional[Question]: Updated question instance if found, None otherwise
        """
        question = self.get_by_id(question_id)
        if not question:
            return None
            
        # Handle question content file upload
        if question_file:
            # Delete old file if exists
            if question.question_content and question.question_type != QuestionType.TEXT:
                delete_file(question.question_content)
            # Save new file
            file_path = save_file(question_file, 'questions')
            data['question_content'] = file_path
            
        # Update question fields
        for key, value in data.items():
            if key not in ['choices', 'correct_answer']:  # Handle these separately
                setattr(question, key, value)
                
        # Update answers based on answer type
        if data.get('answer_type') == AnswerType.MULTIPLE_CHOICE.value or question.answer_type == AnswerType.MULTIPLE_CHOICE:
            if data.get('choices'):
                # Delete existing choices
                for choice in question.choices:
                    if choice.choice_type != ChoiceType.TEXT:
                        delete_file(choice.content)
                question.choices = []
                
                # Validate that at least one choice is marked as correct
                has_correct_choice = False
                for choice_data in data['choices']:
                    if choice_data.get('is_correct'):
                        has_correct_choice = True
                    choice = QuestionChoice(
                        choice_type=ChoiceType(choice_data['type']),
                        content=choice_data['content'],
                        is_correct=choice_data.get('is_correct', False)
                    )
                    question.choices.append(choice)
                    
                if not has_correct_choice:
                    raise BadRequest("At least one choice must be marked as correct")
        else:  # Fill in the blank
            if not data.get('correct_answer'):
                raise BadRequest("Correct answer is required for fill-in-the-blank questions")
            question.correct_answer = data['correct_answer']
        
        try:
            db.session.commit()
            return question
        except SQLAlchemyError as e:
            db.session.rollback()
            raise BadRequest(f"Database error: {str(e)}")
    
    def delete_question(self, question_id: int) -> bool:
        """
        Delete a question and its associated files.
        
        Args:
            question_id: ID of the question to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        question = self.get_by_id(question_id)
        if not question:
            return False
            
        # Delete question content file if exists
        if question.question_content and question.question_type != QuestionType.TEXT:
            delete_file(question.question_content)
            
        # Delete choice files if exist
        for choice in question.choices:
            if choice.choice_type != ChoiceType.TEXT:
                delete_file(choice.content)
                
        try:
            db.session.delete(question)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise BadRequest(f"Database error: {str(e)}")
    
    def get_questions_by_section(self, section_id: int) -> List[Question]:
        """
        Get all questions for a specific section.
        
        Args:
            section_id: ID of the section
            
        Returns:
            List[Question]: List of questions for the specified section
        """
        return self.query().filter_by(section_id=section_id).all() 