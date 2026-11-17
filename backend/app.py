# ============================================================
# Smart Tourist Safety and Emergency Response System
# Flask Application Factory & Server Entrypoint
# ============================================================

import os
import time
from typing import Optional, Type
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from backend.config import Config
from backend.db.connection import check_db_health, close_db_pool
from backend.api import register_blueprints
from backend.notifications.socket_service import socketio, init_socketio
from backend.utils.logger import logger

START_TIME = time.time()
DASHBOARD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard"))

def create_app(config_class: Type[Config] = Config) -> Flask:
    """
    Application factory for the Tourist Safety backend.
    Configures Flask, CORS, SocketIO, API blueprints, and error handlers.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 1. Enable Cross-Origin Resource Sharing (CORS) for Flutter App & Web Dashboard
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=True,
    )

    # 2. Initialize Real-Time WebSocket Service (Flask-SocketIO)
    init_socketio(app, async_mode="threading")

    # 3. Register REST API Blueprints
    register_blueprints(app)

    # 4. Register Core Diagnostic & Status Routes
    register_core_routes(app)

    # 5. Register Standardized JSON Error Handlers
    register_error_handlers(app)

    # 6. Teardown Hooks
    @app.teardown_appcontext
    def teardown_db_context(exception=None):
        if exception:
            logger.error(f"Application context teardown with error: {exception}")

    logger.info("Flask application initialized successfully.")
    return app

def register_core_routes(app: Flask) -> None:
    """Registers root endpoint, dashboard web interface, and system health inspection routes."""

    @app.route("/", methods=["GET"])
    def root():
        return jsonify({
            "service": "Smart Tourist Safety and Emergency Response System API",
            "version": "1.0.0",
            "status": "online",
            "uptime_seconds": round(time.time() - START_TIME, 2),
            "endpoints": {
                "health": "/api/health",
                "tourists": "/api/tourists",
                "location": "/api/location",
                "emergencies": "/api/emergencies",
                "resources": "/api/resources",
                "dashboard": "/api/dashboard",
                "web_dashboard": "/dashboard",
            },
        }), 200

    @app.route("/dashboard", methods=["GET"])
    @app.route("/dashboard/", methods=["GET"])
    @app.route("/dashboard/<path:filename>", methods=["GET"])
    @app.route("/styles.css", methods=["GET"])
    @app.route("/app.js", methods=["GET"])
    def serve_dashboard(filename="index.html"):
        if request.path == "/styles.css":
            return send_from_directory(DASHBOARD_FOLDER, "styles.css")
        if request.path == "/app.js":
            return send_from_directory(DASHBOARD_FOLDER, "app.js")
        return send_from_directory(DASHBOARD_FOLDER, filename)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        db_health = check_db_health()
        overall_status = "healthy" if db_health.get("status") == "healthy" else "degraded"
        
        status_code = 200 if overall_status == "healthy" else 503
        return jsonify({
            "status": overall_status,
            "timestamp": time.time(),
            "uptime_seconds": round(time.time() - START_TIME, 2),
            "database": db_health,
            "environment": {
                "debug": app.config.get("FLASK_DEBUG", False),
                "host": app.config.get("FLASK_HOST", "0.0.0.0"),
                "port": app.config.get("FLASK_PORT", 5000),
            },
        }), status_code

def register_error_handlers(app: Flask) -> None:
    """Enforces consistent JSON error response schema across all endpoints."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad Request",
            "message": getattr(error, "description", "The request payload was invalid or malformed."),
            "status_code": 400,
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not Found",
            "message": f"Endpoint '{request.path}' was not found on this server.",
            "status_code": 404,
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "error": "Method Not Allowed",
            "message": f"Method '{request.method}' is not supported for '{request.path}'.",
            "status_code": 405,
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Unhandled 500 internal error: {error}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing your request.",
            "status_code": 500,
        }), 500

# Application instance for WSGI runners
app = create_app()

if __name__ == "__main__":
    host = Config.FLASK_HOST
    port = Config.FLASK_PORT
    debug = Config.FLASK_DEBUG
    logger.info(f"Starting Smart Tourist Safety server on http://{host}:{port} (debug={debug})...")
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        use_reloader=False,
        allow_unsafe_werkzeug=True,
    )
