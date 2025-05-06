"""
Section service module that handles section-related business logic.
"""
from typing import List, Optional, Dict, Any
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest

from app.models.section import Section
from app.services.base_service import BaseService
from app.utils.file_upload import save_file, delete_file
from app import db
from sqlalchemy.exc import SQLAlchemyError
import os
from app.utils.file_upload import get_upload_folder


class SectionService(BaseService):
    """Service class for handling section-related operations."""
    
    def __init__(self):
        """Initialize the section service."""
        super().__init__(Section)
    
    def create_section(self, data: Dict[str, Any], file: Optional[FileStorage] = None) -> Section:
        """
        Create a new section with optional file upload.
        
        Args:
            data: Dictionary containing section data
            file: Optional file to upload
            
        Returns:
            Section: Created section instance
            
        Raises:
            BadRequest: If required data is missing
        """
        if not data.get('name'):
            raise BadRequest("Section name is required")
            
        if not data.get('level_id'):
            raise BadRequest("Level ID is required")
            
        if file:
            file_path = save_file(file, 'sections')
            data['content_file'] = file_path
            
        return self.create(data)
    
    def update_section(self, section_id: int, data: Dict[str, Any], file: Optional[FileStorage] = None) -> Optional[Section]:
        """
        Update an existing section with optional file upload.
        
        Args:
            section_id: ID of the section to update
            data: Dictionary containing updated section data
            file: Optional new file to upload
            
        Returns:
            Optional[Section]: Updated section instance if found, None otherwise
        """
        section = self.get_by_id(section_id)
        if not section:
            return None
            
        if file:
            # Delete old file if exists
            if section.content_file:
                delete_file(section.content_file)
            # Save new file
            file_path = save_file(file, 'sections')
            data['content_file'] = file_path
            
        return self.update(section_id, data)
    
    def delete_section(self, section_id: int) -> bool:
        """
        Delete a section and its associated file.
        
        Args:
            section_id: ID of the section to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        section = self.get_by_id(section_id)
        if not section:
            return False
            
        # Delete associated file if exists
        if section.content_file:
            delete_file(section.content_file)
            
        return self.delete(section_id)
    
    def get_sections_by_level(self, level_id: int) -> List[Section]:
        """
        Get all sections for a specific level.
        
        Args:
            level_id: ID of the level
            
        Returns:
            List[Section]: List of sections for the specified level
        """
        return self.query().filter_by(level_id=level_id).all()

    @staticmethod
    def get_all():
        sections = Section.query.all()
        return [section.to_dict() for section in sections]

    @staticmethod
    def get_by_id(section_id):
        section = Section.query.get(section_id)
        return section.to_dict() if section else None

    @staticmethod
    def create(data):
        try:
            section = Section(
                name=data['name'],
                description=data.get('description'),
                image=data.get('image'),
                level_id=data['level_id']
            )
            db.session.add(section)
            db.session.commit()
            return section.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {e}")

    @staticmethod
    def update(section_id, data):
        try:
            section = Section.query.get(section_id)
            if not section:
                return None

            # If updating image, delete old image file
            if 'image' in data and section.image:
                try:
                    filename = os.path.basename(section.image)
                    folder = get_upload_folder('sections')
                    old_image_path = os.path.join(folder, filename)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                except Exception as e:
                    print(f"Warning: Failed to delete old image: {e}")

            for key, value in data.items():
                setattr(section, key, value)

            db.session.commit()
            return section.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {e}")

    @staticmethod
    def delete(section_id):
        try:
            section = Section.query.get(section_id)
            if not section:
                return False

            # Delete associated image file
            if section.image:
                try:
                    filename = os.path.basename(section.image)
                    folder = get_upload_folder('sections')
                    image_path = os.path.join(folder, filename)
                    if os.path.exists(image_path):
                        os.remove(image_path)
                except Exception as e:
                    print(f"Warning: Failed to delete image: {e}")

            db.session.delete(section)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {e}") 