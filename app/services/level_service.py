from app.extensions import db
from app.models.level import Level

class LevelService:
    @staticmethod
    def get_all():
        levels = Level.query.all()
        return [level.to_dict() for level in levels]

    @staticmethod
    def get_by_id(level_id):
        level = Level.query.get(level_id)
        if not level:
            raise ValueError('Level not found')
        return level.to_dict()

    @staticmethod
    def create(data):
        if Level.query.filter_by(name=data['name']).first():
            raise ValueError('Level with this name already exists')

        level = Level(
            name=data['name'],
            description=data.get('description'),
            image=data.get('image')
        )
        
        db.session.add(level)
        db.session.commit()
        return level.to_dict()

    @staticmethod
    def update(level_id, data):
        level = Level.query.get(level_id)
        if not level:
            raise ValueError('Level not found')

        if 'name' in data:
            existing_level = Level.query.filter_by(name=data['name']).first()
            if existing_level and existing_level.id != level_id:
                raise ValueError('Level with this name already exists')
            level.name = data['name']

        if 'description' in data:
            level.description = data['description']
        if 'image' in data:
            level.image = data['image']

        db.session.commit()
        return level.to_dict()

    @staticmethod
    def delete(level_id):
        level = Level.query.get(level_id)
        if not level:
            raise ValueError('Level not found')

        db.session.delete(level)
        db.session.commit()
        return {'message': 'Level deleted successfully'} 