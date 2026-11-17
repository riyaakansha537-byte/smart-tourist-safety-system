# ============================================================
# Smart Tourist Safety and Emergency Response System
# Tests: Emergency & SOS Dispatch APIs (Phase 9)
# ============================================================

from unittest.mock import patch
import pytest
from backend.app import create_app
from backend.config import Config
from backend.db.repositories import RecordNotFoundError
from backend.utils.validators import (
    validate_emergency_data,
    validate_status_update_data,
)

class TestEmergencyValidators:
    """Tests emergency payload validation and status update validation."""

    def test_validate_emergency_valid(self):
        payload = {
            "tourist_id": 1,
            "latitude": 15.5553,
            "longitude": 73.7516,
            "incident_type": "CRITICAL_ACCIDENT",
            "priority": 1,
            "description": "Head trauma at beach cliffs",
        }
        is_valid, errors = validate_emergency_data(payload)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_emergency_defaults(self):
        payload = {
            "tourist_id": 2,
            "latitude": 15.4925,
            "longitude": 73.7735,
        }
        is_valid, errors = validate_emergency_data(
            payload,
            default_type="SOS",
            default_priority=2
        )
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_emergency_missing_fields(self):
        is_valid, errors = validate_emergency_data({})
        assert is_valid is False
        assert any("tourist_id" in e for e in errors)
        assert any("latitude" in e for e in errors)
        assert any("longitude" in e for e in errors)

    def test_validate_emergency_invalid_priority(self):
        payload = {
            "tourist_id": 1,
            "latitude": 15.55,
            "longitude": 73.75,
            "incident_type": "SOS",
            "priority": 9,  # invalid priority (> 5)
        }
        is_valid, errors = validate_emergency_data(payload)
        assert is_valid is False
        assert any("priority" in e for e in errors)

    def test_validate_emergency_invalid_type(self):
        payload = {
            "tourist_id": 1,
            "latitude": 15.55,
            "longitude": 73.75,
            "incident_type": "UNREGISTERED_PANIC",
            "priority": 2,
        }
        is_valid, errors = validate_emergency_data(payload)
        assert is_valid is False
        assert any("incident_type" in e for e in errors)

    def test_validate_status_update_valid(self):
        is_valid, errors = validate_status_update_data({"status": "RESOLVED"})
        assert is_valid is True

    def test_validate_status_update_invalid(self):
        is_valid, errors = validate_status_update_data({"status": "FINISHED"})
        assert is_valid is False

class TestEmergencyAPI:
    """Tests Emergency REST API endpoints and Socket.IO hooks."""

    @pytest.fixture
    def client(self):
        app = create_app(Config)
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_ping_emergencies(self, client):
        res = client.get("/api/emergencies/ping")
        assert res.status_code == 200
        data = res.get_json()
        assert data["module"] == "emergencies"
        assert data["status"] == "active"

    @patch("backend.api.emergency_routes.broadcast_emergency_update")
    @patch("backend.api.emergency_routes.EmergencyRepository.create_incident")
    def test_report_accident_success(self, mock_create, mock_broadcast, client):
        mock_create.return_value = {
            "incident_id": 10,
            "tourist_id": 1,
            "incident_type": "CRITICAL_ACCIDENT",
            "priority": 1,
            "status": "RECEIVED",
            "latitude": 15.5553,
            "longitude": 73.7516,
            "description": "Severe road accident",
            "created_at": "2026-10-03T14:10:00Z",
        }
        payload = {
            "tourist_id": 1,
            "latitude": 15.5553,
            "longitude": 73.7516,
            "description": "Severe road accident",
        }
        res = client.post("/api/emergencies/accident", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["status"] == "success"
        assert data["data"]["priority"] == 1
        assert data["data"]["incident_type"] == "CRITICAL_ACCIDENT"
        mock_broadcast.assert_called_once()

    @patch("backend.api.emergency_routes.broadcast_emergency_update")
    @patch("backend.api.emergency_routes.EmergencyRepository.create_incident")
    def test_report_sos_success(self, mock_create, mock_broadcast, client):
        mock_create.return_value = {
            "incident_id": 11,
            "tourist_id": 2,
            "incident_type": "SOS",
            "priority": 2,
            "status": "RECEIVED",
            "latitude": 15.4925,
            "longitude": 73.7735,
            "description": "SOS button tapped on mobile",
        }
        payload = {
            "tourist_id": 2,
            "latitude": 15.4925,
            "longitude": 73.7735,
        }
        res = client.post("/api/emergencies/sos", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["data"]["priority"] == 2
        assert data["data"]["incident_type"] == "SOS"

    @patch("backend.api.emergency_routes.EmergencyRepository.create_incident")
    def test_report_geofence_breach_success(self, mock_create, client):
        mock_create.return_value = {
            "incident_id": 12,
            "tourist_id": 3,
            "incident_type": "DANGEROUS_ZONE",
            "priority": 3,
            "status": "RECEIVED",
            "latitude": 15.0872,
            "longitude": 74.2081,
        }
        payload = {
            "tourist_id": 3,
            "latitude": 15.0872,
            "longitude": 74.2081,
        }
        res = client.post("/api/emergencies/geofence", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["data"]["priority"] == 3

    @patch("backend.api.emergency_routes.EmergencyRepository.create_incident")
    def test_report_safety_alert_success(self, mock_create, client):
        mock_create.return_value = {
            "incident_id": 13,
            "tourist_id": 4,
            "incident_type": "SAFETY_ALERT",
            "priority": 4,
            "status": "RECEIVED",
            "latitude": 15.5030,
            "longitude": 73.9118,
        }
        payload = {
            "tourist_id": 4,
            "latitude": 15.5030,
            "longitude": 73.9118,
        }
        res = client.post("/api/emergencies/safety-alert", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["data"]["priority"] == 4

    def test_emergency_validation_error(self, client):
        res = client.post("/api/emergencies", json={"latitude": "bad_coord"})
        assert res.status_code == 400
        data = res.get_json()
        assert data["error"] == "Validation Error"

    @patch("backend.api.emergency_routes.EmergencyRepository.create_incident")
    def test_emergency_tourist_not_found(self, mock_create, client):
        mock_create.side_effect = RecordNotFoundError("Tourist with ID 999 does not exist.")
        payload = {
            "tourist_id": 999,
            "latitude": 15.55,
            "longitude": 73.75,
        }
        res = client.post("/api/emergencies/sos", json=payload)
        assert res.status_code == 404
        data = res.get_json()
        assert data["error"] == "Not Found"

    @patch("backend.api.emergency_routes.EmergencyRepository.get_incidents")
    def test_list_emergencies(self, mock_get_incidents, client):
        mock_get_incidents.return_value = [
            {"incident_id": 1, "priority": 1, "incident_type": "CRITICAL_ACCIDENT"},
            {"incident_id": 2, "priority": 2, "incident_type": "SOS"},
        ]
        res = client.get("/api/emergencies?status=RECEIVED&limit=20")
        assert res.status_code == 200
        data = res.get_json()
        assert data["count"] == 2
        assert len(data["data"]) == 2

    @patch("backend.api.emergency_routes.EmergencyRepository.get_incident_by_id")
    def test_get_emergency_details_found(self, mock_get_by_id, client):
        mock_get_by_id.return_value = {
            "incident_id": 1,
            "tourist_id": 1,
            "incident_type": "CRITICAL_ACCIDENT",
            "priority": 1,
            "status": "PROCESSING",
            "tourist_name": "Alice Johnson",
            "logs": [
                {"log_id": 1, "action": "INCIDENT_CREATED"},
                {"log_id": 2, "action": "DISPATCH_STARTED"},
            ],
        }
        res = client.get("/api/emergencies/1")
        assert res.status_code == 200
        data = res.get_json()
        assert data["data"]["incident_id"] == 1
        assert len(data["data"]["logs"]) == 2

    @patch("backend.api.emergency_routes.EmergencyRepository.get_incident_by_id")
    def test_get_emergency_details_not_found(self, mock_get_by_id, client):
        mock_get_by_id.return_value = None
        res = client.get("/api/emergencies/999")
        assert res.status_code == 404

    @patch("backend.api.emergency_routes.broadcast_emergency_update")
    @patch("backend.api.emergency_routes.EmergencyRepository.update_incident_status")
    def test_update_incident_status_success(self, mock_update, mock_broadcast, client):
        mock_update.return_value = {
            "incident_id": 1,
            "status": "RESOLVED",
            "resolved_at": "2026-10-03T15:00:00Z",
        }
        payload = {"status": "RESOLVED", "details": "Paramedics treated tourist"}
        res = client.patch("/api/emergencies/1/status", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "RESOLVED"
        mock_broadcast.assert_called_once()

    def test_update_incident_status_validation_error(self, client):
        res = client.patch("/api/emergencies/1/status", json={"status": "INVALID_STATUS"})
        assert res.status_code == 400
        data = res.get_json()
        assert data["error"] == "Validation Error"

    @patch("backend.api.emergency_routes.EmergencyRepository.update_incident_status")
    def test_update_incident_status_not_found(self, mock_update, client):
        mock_update.return_value = None
        res = client.patch("/api/emergencies/999/status", json={"status": "RESOLVED"})
        assert res.status_code == 404
