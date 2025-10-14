from flask import Blueprint, request, jsonify
from ..database import get_db
from ..auth import hash_password, generate_token, auth_required
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    logger = logging.getLogger("market_research_api")
    try:
        data = request.get_json()
        logger.info(f"Register attempt: {data}")
        username = str(data.get("username", "")).strip()
        password = str(data.get("password", "")).strip()
        email = str(data.get("email", "")).strip()
        business_name = str(data.get("business_name", "")).strip()
        if not username or not password or not email:
            logger.warning("Registration failed: missing required fields")
            return jsonify({"error": "Username, password, and email are required"}), 400
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            logger.warning(f"Registration failed: user exists {username} / {email}")
            return jsonify({"error": "Username or email already exists"}), 409
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, email, business_name) VALUES (?, ?, ?, ?)",
            (username, password_hash, email, business_name)
        )
        db.commit()
        user_id = cursor.lastrowid
        token = generate_token(user_id)
        logger.info(f"User registered: {username} ({user_id})")
        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id,
            "token": token
        })
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user or user['password_hash'] != hash_password(password):
            return jsonify({"error": "Invalid username or password"}), 401
        token = generate_token(user['id'])
        return jsonify({
            "message": "Login successful",
            "user_id": user['id'],
            "username": user['username'],
            "business_name": user['business_name'],
            "token": token
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/user-profile', methods=['GET'])
@auth_required
def get_user_profile():
    try:
        user_id = request.user_id
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, username, email, business_name, created_at FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "business_name": user['business_name'],
            "created_at": user['created_at']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
