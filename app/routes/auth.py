
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.database.models.user import User
from app.utils.email import send_verification_email
from app.utils.email import send_verification_email, send_password_reset_email
from app.utils.helpers import generate_verification_code
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime, timedelta
import random
import string

auth_bp = Blueprint('auth', __name__)

#-------------------------------------------------------------

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'username']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if the username already exists
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 400

    try:
        verification_code = generate_verification_code()
        new_user = User(
            email=data['email'],
            username=data['username'],
            verification_code=verification_code,
            verification_code_expires=datetime.utcnow() + timedelta(minutes=30)
        )
        new_user.set_password(data['password'])
        
        # Send verification email
        if not send_verification_email(new_user.email, verification_code):
            return jsonify({'error': 'Failed to send verification email'}), 500

        db.session.add(new_user)
        db.session.commit()
        
        access_token = create_access_token(identity=new_user.id)
        refresh_token = create_refresh_token(identity=new_user.id)
        
        return jsonify({
            'message': 'User registered successfully. Please check your email for verification code.',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'username': new_user.username,
                'is_verified': new_user.is_verified
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

#-------------------------------------------------------------

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('verification_code'):
        return jsonify({'error': 'Email and verification code are required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    if user.is_verified:
        return jsonify({'message': 'Email already verified'}), 200
        
    if not user.verification_code or not user.verification_code_expires:
        return jsonify({'error': 'No verification code found'}), 400
        
    if datetime.utcnow() > user.verification_code_expires:
        return jsonify({'error': 'Verification code has expired'}), 400
        
    if user.verification_code != data['verification_code']:
        return jsonify({'error': 'Invalid verification code'}), 400
    
    user.is_verified = True
    user.verification_code = None
    user.verification_code_expires = None
    db.session.commit()
    
    return jsonify({'message': 'Email verified successfully'}), 200

#-------------------------------------------------------------


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
        
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    if user.is_verified:
        return jsonify({'message': 'Email already verified'}), 200
    
    try:
        verification_code = generate_verification_code()
        user.verification_code = verification_code
        user.verification_code_expires = datetime.utcnow() + timedelta(minutes=30)
        
        if not send_verification_email(user.email, verification_code):
            return jsonify({'error': 'Failed to send verification email'}), 500
            
        db.session.commit()
        return jsonify({'message': 'New verification code sent successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to resend verification code', 'details': str(e)}), 500

#-------------------------------------------------------------

@auth_bp.route('/is-user-email-found', methods=['POST'])
def is_user_email_found():
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    return jsonify({
        'exists': bool(user),
        'is_verified': bool(user and user.is_verified) if user else None
    }), 200

#-------------------------------------------------------------

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        }), 200
    
    return jsonify({'error': 'Invalid email or password'}), 401

#-------------------------------------------------------------

@auth_bp.route('/delete-user', methods=['DELETE'])
def delete_user():
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
        
    try:
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User deleted successfully',
            'deleted_user': {
                'email': user.email,
                'username': user.username
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user', 'details': str(e)}), 500

#-------------------------------------------------------------

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        verification_code = generate_verification_code()
        user.verification_code = verification_code
        user.verification_code_expires = datetime.utcnow() + timedelta(minutes=30)
        
        if not send_password_reset_email(user.email, verification_code):
            return jsonify({'error': 'Failed to send verification email'}), 500    

        db.session.commit()
        return jsonify({'message': 'Verification code sent to your email'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to initiate password reset', 'details': str(e)}), 500

#-------------------------------------------------------------


@auth_bp.route('/retrieve-password', methods=['POST'])
def retrieve_password():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('verification_code') or not data.get('new_password'):
        return jsonify({'error': 'Email, verification code, and new password are required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if datetime.utcnow() > user.verification_code_expires:
        return jsonify({'error': 'Verification code has expired'}), 400
    
    if user.verification_code != data['verification_code']:
        return jsonify({'error': 'Invalid verification code'}), 400
    
    user.set_password(data['new_password'])
    user.verification_code = None
    user.verification_code_expires = None
    db.session.commit()
    
    return jsonify({'message': 'Password updated successfully'}), 200