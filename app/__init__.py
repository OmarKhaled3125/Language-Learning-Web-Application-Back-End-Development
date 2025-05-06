from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'mysql+pymysql://root:root@localhost/language_learning'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret'),
            JWT_ACCESS_TOKEN_EXPIRES=3600,  # 1 hour
            UPLOAD_FOLDER=os.path.join(app.root_path, 'static', 'uploads'),
            MAX_CONTENT_LENGTH=5 * 1024 * 1024,  # 5MB max file size
            ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'gif', 'webp'}
        )
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Ensure upload directories exist
    upload_base = os.path.join(app.root_path, 'static', 'uploads')
    for folder in ['levels', 'sections', 'questions']:
        upload_path = os.path.join(upload_base, folder)
        try:
            os.makedirs(upload_path, exist_ok=True)
        except OSError:
            pass

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)

    # Register blueprints
    from app.controllers.web.page_controller import pages_bp
    from app.controllers.api.auth_controller import auth_bp
    from app.controllers.api.level_controller import level_bp
    from app.controllers.api.section_controller import section_bp
    from app.controllers.api.question_controller import question_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(level_bp, url_prefix='/api/level')
    app.register_blueprint(section_bp, url_prefix='/api/section')
    app.register_blueprint(question_bp, url_prefix='/api/question')

    return app 