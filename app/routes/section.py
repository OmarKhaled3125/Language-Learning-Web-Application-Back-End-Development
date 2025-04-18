from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from app.models.section import Section
from app.models.level import Level
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

section_bp = Blueprint('section', __name__, url_prefix='/api/sections')

@section_bp.route('/', methods=['GET'])
def get_sections():
    sections = Section.query.all()
    return jsonify([section.to_dict() for section in sections])

@section_bp.route('/<int:section_id>', methods=['GET'])
def get_section(section_id):
    section = Section.query.get_or_404(section_id)
    return jsonify(section.to_dict())

@section_bp.route('/', methods=['POST'])
@jwt_required()
def create_section():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required_fields = ['name', 'level_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    level = Level.query.get(data['level_id'])
    if not level:
        return jsonify({'error': 'Level not found'}), 404

    section = Section(
        name=data['name'],
        description=data.get('description'),
        image=data.get('image'),
        level_id=data['level_id']
    )

    db.session.add(section)
    db.session.commit()

    return jsonify(section.to_dict()), 201

@section_bp.route('/<int:section_id>', methods=['PUT'])
@jwt_required()
def update_section(section_id):
    section = Section.query.get_or_404(section_id)
    data = request.get_json()

    if 'name' in data:
        section.name = data['name']
    if 'description' in data:
        section.description = data['description']
    if 'image' in data:
        section.image = data['image']
    if 'level_id' in data:
        level = Level.query.get(data['level_id'])
        if not level:
            return jsonify({'error': 'Level not found'}), 404
        section.level_id = data['level_id']

    db.session.commit()
    return jsonify(section.to_dict())

@section_bp.route('/<int:section_id>', methods=['DELETE'])
@jwt_required()
def delete_section(section_id):
    section = Section.query.get_or_404(section_id)
    db.session.delete(section)
    db.session.commit()
    return '', 204

# Web routes
@section_bp.route('/web', methods=['GET'])
def sections_page():
    sections = Section.query.all()
    return render_template('sections/index.html', sections=sections)

@section_bp.route('/web/create', methods=['GET', 'POST'])
@jwt_required()
def create_section_page():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        image = request.form.get('image')
        level_id = request.form.get('level_id')

        if not name or not level_id:
            flash('Name and level are required', 'error')
            return redirect(url_for('section.create_section_page'))

        section = Section(
            name=name,
            description=description,
            image=image,
            level_id=level_id
        )

        db.session.add(section)
        db.session.commit()
        flash('Section created successfully', 'success')
        return redirect(url_for('section.sections_page'))

    levels = Level.query.all()
    return render_template('sections/create.html', levels=levels)

@section_bp.route('/web/<int:section_id>/edit', methods=['GET', 'POST'])
@jwt_required()
def edit_section_page(section_id):
    section = Section.query.get_or_404(section_id)
    
    if request.method == 'POST':
        section.name = request.form.get('name')
        section.description = request.form.get('description')
        section.image = request.form.get('image')
        section.level_id = request.form.get('level_id')

        db.session.commit()
        flash('Section updated successfully', 'success')
        return redirect(url_for('section.sections_page'))

    levels = Level.query.all()
    return render_template('sections/edit.html', section=section, levels=levels)