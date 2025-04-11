from flask import Blueprint, request, jsonify, abort
from app.extensions import db
from app.database.models.levels import Level, Category, Option

levels_bp = Blueprint('levels', __name__)

#-------------------------------------------------------------------

@levels_bp.route('/levels', methods=['GET'])
def get_levels():
    levels = Level.query.all()
    if not levels:
        abort(404, description="No levels found")
    return jsonify([{"id": level.id, "name": level.name} for level in levels])

#-------------------------------------------------------------------

@levels_bp.route('/levels/<int:level_id>/categories', methods=['GET'])
def get_categories(level_id):
    categories = Category.query.filter_by(level_id=level_id).all()
    if not categories:
        abort(404, description=f"No categories found for level {level_id}")
    return jsonify([{"id": category.id, "title": category.title} for category in categories])

#-------------------------------------------------------------------

@levels_bp.route('/levels/<int:level_id>/categories/<int:category_id>/options', methods=['GET'])
def get_options(level_id, category_id):
    options = Option.query.filter_by(category_id=category_id).all()
    if not options:
        abort(404, description=f"No options found for category {category_id}")
    return jsonify([{"id": option.id, "name": option.name} for option in options])