import os
from dotenv import load_dotenv

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from models import db
from routes import tasks_bp, missions_bp

# Load environment variables from backend/.env and allow override
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)

# Configure Flask to point to the React frontend production build folder
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
app = Flask(__name__, static_folder=frontend_dist, static_url_path="/")
app.config.from_object(Config)

# Enable CORS for frontend and API clients
CORS(app, resources={r"/*": {"origins": "*"}})

# Bind SQLAlchemy to the app
db.init_app(app)

# Register Blueprints under root prefix (spec requirements)
app.register_blueprint(tasks_bp, name='tasks_root', url_prefix='/')
app.register_blueprint(missions_bp, name='missions_root', url_prefix='/')

# Register Blueprints under '/api' prefix (frontend/integration compatibility)
app.register_blueprint(tasks_bp, name='tasks_api', url_prefix='/api')
app.register_blueprint(missions_bp, name='missions_api', url_prefix='/api')

# Ensure database tables are created
with app.app_context():
    db.create_all()

@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    log_path = os.path.join(os.path.dirname(__file__), "error.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("=== EXCEPTION ===\n")
        traceback.print_exc(file=f)
    traceback.print_exc()
    return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health():
    import sys
    return jsonify({
        "status": "healthy",
        "service": "QuestFlow AI Backend Blueprint Router",
        "pid": os.getpid(),
        "cwd": os.getcwd(),
        "file": __file__,
        "python": sys.version,
        "api_key_configured": bool(Config.GEMINI_API_KEY),
        "api_key_last4": Config.GEMINI_API_KEY[-4:] if Config.GEMINI_API_KEY else None
    }), 200

# Serve static files and frontend routes in production
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path.startswith("api") or path.startswith("health"):
        return "Not Found", 404
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return app.send_static_file(path)
    else:
        return app.send_static_file('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("BACKEND_PORT", os.environ.get("PORT", 5000)))
    app.run(host="0.0.0.0", port=port, debug=False)