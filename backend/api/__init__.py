# ============================================================
# Smart Tourist Safety and Emergency Response System
# API Blueprints Registration
# ============================================================

from flask import Flask
from backend.api.tourist_routes import tourist_bp
from backend.api.location_routes import location_bp
from backend.api.emergency_routes import emergency_bp
from backend.api.resource_routes import resource_bp
from backend.api.dashboard_routes import dashboard_bp
from backend.utils.logger import logger

def register_blueprints(app: Flask) -> None:
    """Registers all REST API blueprints with appropriate url prefixes."""
    app.register_blueprint(tourist_bp, url_prefix="/api/tourists")
    app.register_blueprint(location_bp, url_prefix="/api/location")
    app.register_blueprint(emergency_bp, url_prefix="/api/emergencies")
    app.register_blueprint(resource_bp, url_prefix="/api/resources")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    logger.info("All 5 REST API blueprints registered successfully under /api/*.")
