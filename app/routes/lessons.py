from flask import Blueprint, request, jsonify, abort
import random
from app.extensions import db
from app.database.models.lessons import Lesson

lessons_bp = Blueprint('lessons', __name__)

#-------------------------------------------------------------------

@lessons_bp.route('/lessons', methods=['GET'])
def get_lessons():
    level_id = request.args.get('level_id', type=int)
    category_id = request.args.get('category_id', type=int)
    option_id = request.args.get('option_id', type=int)
    lesson_number = request.args.get('lesson_number', type=int) 

    query = Lesson.query
    if level_id:
        query = query.filter_by(level_id=level_id)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if option_id:
        query = query.filter_by(option_id=option_id)
    if lesson_number:  
        query = query.filter_by(lesson_number=lesson_number)

    lessons = query.order_by(Lesson.lesson_number).all()
    if not lessons:
        abort(404, description="No lessons found matching the criteria")
    return jsonify([lesson.to_dict() for lesson in lessons])

#-------------------------------------------------------------------
