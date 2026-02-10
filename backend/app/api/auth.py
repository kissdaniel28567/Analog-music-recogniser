from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Cartridge
from ..extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400
        
    new_user = User(
        username=username, 
        password_hash=generate_password_hash(password, method='scrypt')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Default cartridge might leave it for the final version
    default_cart = Cartridge(name="Default Cartridge", user_id=new_user.id, is_active_on_turntable=True)
    db.session.add(default_cart)
    db.session.commit()
    
    return jsonify({"message": "Registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and check_password_hash(user.password_hash, data.get('password')):
        login_user(user)
        return jsonify({"message": "Login successful", "user_id": user.id})
        
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"})

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        "username": current_user.username, 
        "id": current_user.id
    })