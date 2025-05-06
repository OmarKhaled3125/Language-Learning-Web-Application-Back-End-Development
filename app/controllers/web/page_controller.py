from flask import Blueprint, render_template, request

# Create the blueprint
pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def home():
    return render_template('home.html')

@pages_bp.route('/levels/')
def levels_page():
    return render_template('levels.html')

@pages_bp.route('/sections')
def sections_page():
    level_id = request.args.get('level_id')
    if not level_id:
        return render_template('error.html', message='Level ID is required'), 400
    return render_template('sections.html')

@pages_bp.route('/questions')
def questions_page():
    section_id = request.args.get('section_id')
    if not section_id:
        return render_template('error.html', message='Section ID is required'), 400
    return render_template('questions.html')

@pages_bp.route('/login')
def login_page():
    return render_template('login.html')
