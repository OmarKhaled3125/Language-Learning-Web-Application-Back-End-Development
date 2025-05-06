from typing import List, Optional, Dict, Any
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest
import json
from flask import request

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
    
    def get_all(self) -> List[Question]:
        return self.query().all()

    def get_by_id(self, question_id: int) -> Optional[Question]:
        return self.query().get(question_id)

    def get_questions_by_section(self, section_id: int) -> List[Question]:
        return self.query().filter_by(section_id=section_id).all()

    def create_question(self, data, question_file=None, files=None):
        # Parse choices
        choices = data.get('choices')
        if choices and isinstance(choices, str):
            choices = json.loads(choices)
        elif not choices:
            choices = []

        # Validate enums
        try:
            qtype = QuestionType(data['question_type'])
            atype = AnswerType(data['answer_type'])
        except Exception:
            raise BadRequest("Invalid question_type or answer_type")

        # Handle question content file
        if qtype in [QuestionType.IMAGE, QuestionType.AUDIO]:
            if not question_file:
                raise BadRequest("Question file is required for image/audio type")
            file_path = save_file(question_file, 'questions')
            question_content = file_path
        else:
            question_content = data.get('question_content')
            if not question_content:
                raise BadRequest("Question content is required")

        # Create question
        question = Question(
            section_id=data['section_id'],
            question_type=qtype,
            question_content=question_content,
            answer_type=atype,
            correct_answer=data.get('correct_answer')
        )

        # Handle choices
        if atype == AnswerType.MULTIPLE_CHOICE and choices:
            has_correct = False
            for idx, choice_data in enumerate(choices):
                if choice_data.get('is_correct', False):
                    has_correct = True
            if not has_correct:
                raise BadRequest("At least one choice must be marked as correct")
        elif atype == AnswerType.FILL_IN_BLANK:
            if not data.get('correct_answer'):
                raise BadRequest("Correct answer is required for fill-in-the-blank questions")

        try:
            db.session.add(question)
            db.session.commit()
            return question
        except SQLAlchemyError as e:
            db.session.rollback()
            print("Database error:", e)
            raise BadRequest(f"Database error: {str(e)}")
    
    def update_question(self, question_id: int, data: Dict[str, Any], question_file: Optional[FileStorage] = None) -> Optional[Question]:
        question = self.get_by_id(question_id)
        if not question:
            return None
        
        # Handle question content file upload
        if data.get('question_type') in ['image', 'audio']:
            if question_file:
                # Delete old file if exists
                if question.question_content and question.question_type != QuestionType.TEXT:
                    delete_file(question.question_content)
                # Save new file
                file_path = save_file(question_file, 'questions')
                data['question_content'] = file_path
            elif not data.get('question_content'):
                raise BadRequest("Question file is required for image/audio type")
        
        # Update question fields
        for key, value in data.items():
            if key not in ['choices', 'correct_answer']:
                setattr(question, key, value)
        
        # Handle choices for multiple choice
        if data.get('answer_type') == AnswerType.MULTIPLE_CHOICE.value or question.answer_type == AnswerType.MULTIPLE_CHOICE:
            if data.get('choices'):
                choices = json.loads(data['choices'])
                # Delete existing choices and their files if needed
                for choice in question.choices:
                    if choice.choice_type != ChoiceType.TEXT:
                        delete_file(choice.content)
                question.choices = []
                # Add new choices
                for choice_data in choices:
                    if choice_data['type'] in ['image', 'audio']:
                        file_key = choice_data['content']
                        file = request.files.get(file_key)
                        if file:
                            file_path = save_file(file, 'questions')
                            choice_data['content'] = file_path
                    choice = QuestionChoice(
                        choice_type=ChoiceType(choice_data['type']),
                        content=choice_data['content'],
                        is_correct=choice_data.get('is_correct', False)
                    )
                    question.choices.append(choice)
                # Validate at least one correct choice
                if not any(c.get('is_correct', False) for c in choices):
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
            print("Database error:", e)
            raise BadRequest(f"Database error: {str(e)}")
    
    def delete_question(self, question_id: int) -> bool:
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
            print("Database error:", e)
            raise BadRequest(f"Database error: {str(e)}")
    
    def add_choices(self, question_id, data, files=None):
        question = self.get_by_id(question_id)
        if not question:
            raise BadRequest("Question not found")
        choices = data.get('choices')
        if choices and isinstance(choices, str):
            choices = json.loads(choices)
        elif not choices:
            choices = []
        new_choices = []
        for choice_data in choices:
            try:
                ctype = ChoiceType(choice_data['type'])
            except Exception:
                raise BadRequest("Invalid choice type")
            content = choice_data['content']
            if ctype in [ChoiceType.IMAGE, ChoiceType.AUDIO]:
                file = files.get(content) if files else None
                if not file:
                    raise BadRequest(f"File for choice {content} is missing")
                content = save_file(file, 'questions')
            is_correct = choice_data.get('is_correct', False)
            choice = QuestionChoice(
                question_id=question_id,
                choice_type=ctype,
                content=content,
                is_correct=is_correct
            )
            db.session.add(choice)
            new_choices.append(choice)
        db.session.commit()
        return new_choices


    def delete_choice(self, question_id, choice_id):
        choice = QuestionChoice.query.filter_by(id=choice_id, question_id=question_id).first()
        if not choice:
            raise BadRequest("Choice not found")
        db.session.delete(choice)
        db.session.commit()

    def add_single_choice(self, question_id, data, files=None):
        question = self.get_by_id(question_id)
        if not question:
            raise BadRequest("Question not found")
        try:
            ctype = ChoiceType(data['choice_type'])
        except Exception:
            raise BadRequest("Invalid choice type")
        content = data.get('content')
        if ctype in [ChoiceType.IMAGE, ChoiceType.AUDIO]:
            file = files.get('content') if files else None
            if not file:
                raise BadRequest("File for choice content is missing")
            content = save_file(file, 'questions')
        is_correct = data.get('is_correct', 'false').lower() == 'true'
        choice = QuestionChoice(
            question_id=question_id,
            choice_type=ctype,
            content=content,
            is_correct=is_correct
        )
        db.session.add(choice)
        db.session.commit()
        return choice

    def update_single_choice(self, question_id, choice_id, data, files=None):
        choice = QuestionChoice.query.filter_by(id=choice_id, question_id=question_id).first()
        if not choice:
            raise BadRequest("Choice not found")
        try:
            if 'choice_type' in data:
                ctype = ChoiceType(data['choice_type'])
                choice.choice_type = ctype
            if 'is_correct' in data:
                choice.is_correct = str(data['is_correct']).lower() == 'true'
            if 'content' in data:
                content = data['content']
                if choice.choice_type in [ChoiceType.IMAGE, ChoiceType.AUDIO]:
                    file = files.get('content') if files else None
                    if file:
                        # Delete old file if exists
                        if choice.content:
                            delete_file(choice.content)
                        content = save_file(file, 'questions')
                    else:
                        # If no new file, keep the old content
                        content = choice.content
                choice.content = content
            db.session.commit()
            return choice
        except Exception as e:
            db.session.rollback()
            print("Error updating choice:", e)
            raise BadRequest(f"Failed to update choice: {str(e)}")
