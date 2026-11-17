
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
