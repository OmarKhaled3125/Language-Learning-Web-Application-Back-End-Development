from app.extensions import db
from app.models.level import Level
from sqlalchemy.exc import SQLAlchemyError
import os

class LevelService:
    @staticmethod
    def get_all():
        levels = Level.query.all()
        return [level.to_dict() for level in levels]

    @staticmethod
    def get_by_id(level_id):
        level = Level.query.get(level_id)
        return level.to_dict() if level else None

    @staticmethod
    def create(data):
        try:
            level = Level(
                name=data['name'],
                description=data.get('description', ''),
                image_url=data.get('image_url')
            )
            db.session.add(level)
            db.session.commit()
            return level.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")

    @staticmethod
    def update(level_id, data):
        try:
            level = Level.query.get(level_id)
            if not level:
                return None
            
            # If updating image, delete old image if exists
            if 'image_url' in data and level.image_url:
                try:
                    old_image_path = os.path.join(os.getcwd(), 'app', level.image_url.lstrip('/'))
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                except Exception as e:
                    print(f"Warning: Failed to delete old image: {str(e)}")
            
            # Update fields
            for key, value in data.items():
                setattr(level, key, value)
            
            db.session.commit()
            return level.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}")

    @staticmethod
    def delete(level_id):
        try:
            level = Level.query.get(level_id)
            if not level:
                return False
            
            # Delete associated image if exists
            if level.image_url:
                try:
                    image_path = os.path.join(os.getcwd(), 'app', level.image_url.lstrip('/'))
                    if os.path.exists(image_path):
                        os.remove(image_path)
                except Exception as e:
                    print(f"Warning: Failed to delete image: {str(e)}")
            
            db.session.delete(level)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Database error: {str(e)}") 