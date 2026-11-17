# ============================================================
# Smart Tourist Safety and Emergency Response System
# Tests: Flask Backend Foundation (Phase 6)
# ============================================================

import pytest
from unittest.mock import patch
from backend.app import create_app
from backend.config import Config

class TestFlaskFoundation:
    """Validates Flask app factory, blueprints, routing, error handlers, and CORS."""

    @pytest.fixture
    def client(self):
        """Creates a test client for the application."""
        app = create_app(Config)
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "online"
        assert "endpoints" in data
        assert "/api/health" in data["endpoints"].values()
        assert "/api/tourists" in data["endpoints"].values()

    @patch("backend.app.check_db_health")
    def test_health_check_healthy(self, mock_health, client):
        mock_health.return_value = {
            "status": "healthy",
            "database": "tourist_safety_db",
            "user": "tourist_admin",
            "pool_closed": False,
        }
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data
        assert data["database"]["status"] == "healthy"

    @patch("backend.app.check_db_health")
    def test_health_check_degraded(self, mock_health, client):
        mock_health.return_value = {
            "status": "unhealthy",
            "error": "connection refused",
            "pool_closed": True,
        }
        response = client.get("/api/health")
        assert response.status_code == 503
        data = response.get_json()
        assert data["status"] == "degraded"

    def test_blueprint_ping_endpoints(self, client):
        endpoints = [
            "/api/tourists/ping",
            "/api/location/ping",
            "/api/emergencies/ping",
            "/api/resources/ping",
            "/api/dashboard/ping",
        ]
        for ep in endpoints:
            res = client.get(ep)
            assert res.status_code == 200, f"Failed for endpoint {ep}"
            json_data = res.get_json()
            assert json_data["status"] == "active"

    def test_404_not_found_handler(self, client):
        response = client.get("/api/invalid-non-existent-route")
        assert response.status_code == 404
        data = response.get_json()
        assert data["error"] == "Not Found"
        assert data["status_code"] == 404

    def test_405_method_not_allowed_handler(self, client):
        # Root only supports GET, so POST should trigger 405
        response = client.post("/")
        assert response.status_code == 405
        data = response.get_json()
        assert data["error"] == "Method Not Allowed"
        assert data["status_code"] == 405

    def test_cors_headers_present(self, client):
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers

    def test_dashboard_endpoint(self, client):
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert b"TOURIST SAFETY COMMAND" in response.data
