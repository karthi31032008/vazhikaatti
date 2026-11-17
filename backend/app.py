
from flask import Flask, jsonify, send_from_directory, request, session
from database import create_tables, get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY environment variable is required")

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)

create_tables()

# Login protection
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Please login first"}), 401
        return func(*args, **kwargs)
    return wrapper


# Role-based access protection
def role_required(*allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return jsonify({"error": "Please login first"}), 401

            if session.get("role") not in allowed_roles:
                return jsonify({"error": "Access denied"}), 403

            return func(*args, **kwargs)
        return wrapper
    return decorator


# User registration (public registration creates USER only)
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    if len(name) > 100 or len(email) > 150:
        return jsonify({"error": "Input is too long"}), 400

    if "@" not in email or "." not in email:
        return jsonify({"error": "Enter a valid email"}), 400

    password_hash = generate_password_hash(password)

    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, 'user')
        """, (name, email, password_hash))
        conn.commit()
    except Exception:
        conn.close()
        return jsonify({"error": "Email may already be registered"}), 409

    conn.close()
    return jsonify({"success": True, "message": "Registration successful"}), 201


# Login
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    conn = get_db_connection()
    user = conn.execute(
        "SELECT id, name, email, password_hash, role FROM users WHERE email = ?",
        (email,)
    ).fetchone()
    conn.close()

    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    session.clear()
    session["user_id"] = user["id"]
    session["role"] = user["role"]

    dashboards = {
        "user": "user-dashboard.html",
        "worker": "worker-dashboard.html",
        "admin": "admin-dashboard.html"
    }

    return jsonify({
        "success": True,
        "role": user["role"],
        "dashboard": dashboards.get(user["role"], "index.html")
    })


# Logout
@app.route("/api/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out"})


# Current logged-in account
@app.route("/api/me", methods=["GET"])
@login_required
def current_user():
    conn = get_db_connection()
    user = conn.execute(
        "SELECT id, name, email, role FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()
    conn.close()

    if user is None:
        session.clear()
        return jsonify({"error": "Account not found"}), 404

    return jsonify(dict(user))


# Homepage
@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


# Frontend pages and files
@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# Get services from SQLite
@app.route("/api/services")
def services():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM services").fetchall()
    conn.close()

    return jsonify({
        "services": [dict(row) for row in rows]
    })


# Backend health check
@app.route("/api/health")
def health():
    return jsonify({
        "status": "Running successfully",
        "database": "Connected"
    })


# Submit a new complaint
@app.route("/api/complaints", methods=["POST"])
def submit_complaint():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid request data"}), 400

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    title = str(data.get("category", "")).strip()
    location = str(data.get("location", "")).strip()
    description = str(data.get("description", "")).strip()

    if not all([name, email, title, location, description]):
        return jsonify({
            "error": "Please complete all required fields"
        }), 400

    if len(name) > 100 or len(email) > 150:
        return jsonify({"error": "Input is too long"}), 400

    if "@" not in email or "." not in email:
        return jsonify({"error": "Enter a valid email address"}), 400

    if len(title) > 100 or len(location) > 200:
        return jsonify({"error": "Input is too long"}), 400

    if len(description) > 2000:
        return jsonify({"error": "Description is too long"}), 400

    conn = get_db_connection()

    cursor = conn.execute("""
        INSERT INTO complaints
        (name, email, title, location, description)
        VALUES (?, ?, ?, ?, ?)
    """, (name, email, title, location, description))

    complaint_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Complaint submitted successfully",
        "complaint_id": complaint_id,
        "status": "Pending"
    }), 201


# Track complaint status
@app.route("/api/complaints/<int:complaint_id>", methods=["GET"])
def track_complaint(complaint_id):
    conn = get_db_connection()

    complaint = conn.execute("""
        SELECT id, status, created_at
        FROM complaints
        WHERE id = ?
    """, (complaint_id,)).fetchone()

    conn.close()

    if complaint is None:
        return jsonify({
            "error": "Complaint not found"
        }), 404

    return jsonify({
        "complaint_id": complaint["id"],
        "status": complaint["status"],
        "created_at": complaint["created_at"]
    })


if __name__ == "__main__":
    app.run(debug=True)
