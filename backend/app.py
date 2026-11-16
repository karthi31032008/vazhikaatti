
from flask import Flask, jsonify
from database import create_tables, get_db_connection

app = Flask(__name__)

# Create database tables
create_tables()

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to VazhiKaatti!",
        "status": "Backend and Database Connected Successfully"
    })

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

@app.route("/api/health")
def health():
    return jsonify({
        "status": "OK",
        "database": "Connected"
    })

if __name__ == "__main__":
    app.run(debug=True)
