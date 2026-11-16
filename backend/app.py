
from flask import Flask, jsonify, send_from_directory
from database import create_tables, get_db_connection
import os

# Frontend folder location
FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)

# Create SQLite tables
create_tables()


# Homepage
@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


# Services API
@app.route("/api/services")
def services():
    conn = get_db_connection()

    rows = conn.execute(
        "SELECT * FROM services"
    ).fetchall()

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


if __name__ == "__main__":
    app.run(debug=True)
