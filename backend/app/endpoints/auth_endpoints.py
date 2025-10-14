from flask import Blueprint, request, jsonify
from ..database import get_db
from ..auth import hash_password, generate_token, auth_required

auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")
        business_name = data.get("business_name", "")
        if not username or not password or not email:
            return jsonify({"error": "Username, password, and email are required"}), 400
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({"error": "Username or email already exists"}), 409
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, email, business_name) VALUES (?, ?, ?, ?)",
            (username, password_hash, email, business_name)
        )
        db.commit()
        user_id = cursor.lastrowid
        token = generate_token(user_id)
        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id,
            "token": token
        })
    except Exception as e:
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
