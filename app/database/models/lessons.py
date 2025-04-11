from app.extensions import db
from datetime import datetime

class Lesson(db.Model):
    __tablename__ = 'lessons'

#-------------------------------------------------------------------

    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=False)
    lesson_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    audio_url = db.Column(db.String(300))
    image_url = db.Column(db.String(300))
    quiz_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

#-------------------------------------------------------------------

    # Relationships
    level = db.relationship('Level', backref='lessons')
    category = db.relationship('Category', backref='lessons')
    option = db.relationship('Option', backref='lessons')

#-------------------------------------------------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "level": self.level.name if self.level else None,
            "category": self.category.title if self.category else None,
            "option": self.option.name if self.option else None,
            "lesson_number": self.lesson_number,
            "title": self.title,
            "content": self.content,
            "audio_url": self.audio_url,
            "image_url": self.image_url,
            "quiz_data": self.quiz_data,
        }