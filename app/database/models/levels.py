from app.extensions import db

#-------------------------------------------------------------------

class Level(db.Model):
    __tablename__ = 'levels'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    categories = db.relationship('Category', backref='level', lazy=True, cascade='all, delete-orphan')

#-------------------------------------------------------------------

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id'), nullable=False)
    learning_options = db.relationship('Option', backref='category', lazy=True, cascade='all, delete-orphan')

#-------------------------------------------------------------------

class Option(db.Model):
    __tablename__ = 'options'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)