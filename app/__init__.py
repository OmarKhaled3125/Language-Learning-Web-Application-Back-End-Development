from flask import Flask
from app.config import Config
from app.extensions import db, jwt, mail
from app.routes.auth import auth_bp
from app.routes.general import general_bp
from app.routes.level import level_bp
from app.routes.pages import pages_bp
from app.routes.section import section_bp
from flask_migrate import Migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(general_bp)
    app.register_blueprint(level_bp, url_prefix='/api/levels')
    app.register_blueprint(pages_bp)
    app.register_blueprint(section_bp, url_prefix='/api/sections')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app