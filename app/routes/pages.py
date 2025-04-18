from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def home():
    return render_template('home.html')

@pages_bp.route('/levels/')
def levels_page():
    return render_template('levels.html')

@pages_bp.route('/login')
def login_page():
    return render_template('login.html')

@pages_bp.route('/sections')
def sections_page():
    return render_template('sections.html') 


