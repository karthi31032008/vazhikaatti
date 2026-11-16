from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to VazhiKaatti!",
        "status": "Running successfully"
    })

@app.route("/api/services")
def services():
    return jsonify({
        "services": [
            "Local Services",
            "Community Updates",
            "Report Issues",
            "Connect People"
        ]
    })

if __name__ == "__main__":
    app.run()
