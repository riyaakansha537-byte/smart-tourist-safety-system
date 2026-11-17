# ============================================================
# Smart Tourist Safety and Emergency Response System
# Tests: Resource & Dashboard REST APIs (Phases 15, 16)
# ============================================================

from unittest.mock import MagicMock, patch
import pytest
from backend.app import create_app
from backend.config import Config

class TestResourceAPI:
    """Tests Resource & Team management REST endpoints."""

    @pytest.fixture
    def client(self):
        app = create_app(Config)
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_ping_resources(self, client):
        res = client.get("/api/resources/ping")
        assert res.status_code == 200
        data = res.get_json()
        assert data["module"] == "resources"

    @patch("backend.api.resource_routes.ResourceRepository.get_all_resources")
    def test_list_resources(self, mock_get_all, client):
        mock_get_all.return_value = [
            {"resource_id": 1, "resource_name": "Ambulance-1", "status": "AVAILABLE"},
            {"resource_id": 2, "resource_name": "Copter-1", "status": "ASSIGNED"},
        ]
        res = client.get("/api/resources?type=AMBULANCE")
        assert res.status_code == 200
        data = res.get_json()
        assert data["count"] == 2

    @patch("backend.api.resource_routes.ResourceRepository.get_available_resources")
    def test_list_available_resources(self, mock_avail, client):
        mock_avail.return_value = [
            {"resource_id": 1, "resource_name": "Ambulance-1", "status": "AVAILABLE"}
        ]
        res = client.get("/api/resources/available")
        assert res.status_code == 200
        data = res.get_json()
        assert data["count"] == 1

    @patch("backend.api.resource_routes.ResourceRepository.get_resource_by_id")
    def test_get_resource_found(self, mock_get_id, client):
        mock_get_id.return_value = {"resource_id": 1, "resource_name": "Ambulance-1"}
        res = client.get("/api/resources/1")
        assert res.status_code == 200
        assert res.get_json()["data"]["resource_id"] == 1

    @patch("backend.api.resource_routes.ResourceRepository.get_resource_by_id")
    def test_get_resource_not_found(self, mock_get_id, client):
        mock_get_id.return_value = None
        res = client.get("/api/resources/999")
        assert res.status_code == 404

    @patch("backend.api.resource_routes.RescueTeamRepository.get_all_teams")
    def test_list_teams(self, mock_teams, client):
        mock_teams.return_value = [{"team_id": 1, "team_name": "Alpha Paramedic"}]
        res = client.get("/api/resources/teams")
        assert res.status_code == 200
        assert res.get_json()["count"] == 1

    @patch("backend.api.resource_routes.RescueTeamRepository.get_available_teams")
    def test_list_available_teams(self, mock_avail_teams, client):
        mock_avail_teams.return_value = [{"team_id": 1, "status": "AVAILABLE"}]
        res = client.get("/api/resources/teams/available")
        assert res.status_code == 200
        assert res.get_json()["count"] == 1

    @patch("backend.api.resource_routes.resource_manager.request_allocation")
    def test_allocate_resources_safe_success(self, mock_request_alloc, client):
        mock_request_alloc.return_value = {
            "allocated": True,
            "incident_id": 10,
            "safe_sequence": [10],
        }
        payload = {"incident_id": 10, "demands": {"AMBULANCE": 1}}
        res = client.post("/api/resources/allocate", json=payload)
        assert res.status_code == 200
        assert res.get_json()["allocated"] is True

    @patch("backend.api.resource_routes.resource_manager.request_allocation")
    def test_allocate_resources_unsafe_denied(self, mock_request_alloc, client):
        mock_request_alloc.return_value = {
            "allocated": False,
            "incident_id": 10,
            "reason": "Deadlock avoidance: leads to unsafe state",
            "status_code": 409,
        }
        payload = {"incident_id": 10, "demands": {"AMBULANCE": 3}}
        res = client.post("/api/resources/allocate", json=payload)
        assert res.status_code == 409
        assert res.get_json()["allocated"] is False

    @patch("backend.api.resource_routes.resource_manager.release_allocation")
    def test_release_resources(self, mock_release, client):
        mock_release.return_value = {
            "status": "success",
            "incident_id": 10,
            "released_assignments": 1,
        }
        res = client.post("/api/resources/release", json={"incident_id": 10})
        assert res.status_code == 200
        assert res.get_json()["status"] == "success"

    @patch("backend.api.resource_routes.ResourceRepository.get_incident_assignments")
    def test_get_assignments(self, mock_asgns, client):
        mock_asgns.return_value = [{"assignment_id": 1, "incident_id": 10}]
        res = client.get("/api/resources/assignments/10")
        assert res.status_code == 200
        assert res.get_json()["count"] == 1

class TestDashboardAPI:
    """Tests Authority Dashboard aggregation REST endpoints."""

    @pytest.fixture
    def client(self):
        app = create_app(Config)
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_ping_dashboard(self, client):
        res = client.get("/api/dashboard/ping")
        assert res.status_code == 200
        data = res.get_json()
        assert data["module"] == "dashboard"

    @patch("backend.api.dashboard_routes.DashboardRepository.get_summary_counts")
    def test_dashboard_summary(self, mock_counts, client):
        mock_counts.return_value = {
            "total_tourists": 25,
            "active_incidents": 3,
            "available_resources": 5,
            "available_teams": 4,
        }
        res = client.get("/api/dashboard/summary")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        metrics = data["metrics"]
        assert metrics["total_tourists"] == 25
        assert metrics["active_incidents"] == 3
        assert "is_safe_state" in metrics

    @patch("backend.api.dashboard_routes.EmergencyRepository.get_incidents")
    def test_dashboard_active_emergencies(self, mock_incidents, client):
        mock_incidents.return_value = [
            {"incident_id": 1, "status": "PROCESSING", "priority": 1},
            {"incident_id": 2, "status": "RESOLVED", "priority": 2},
        ]
        res = client.get("/api/dashboard/active-emergencies")
        assert res.status_code == 200
        data = res.get_json()
        # Only active (non-resolved) included
        assert data["count"] == 1
        assert data["data"][0]["incident_id"] == 1

    @patch("backend.api.dashboard_routes.LogRepository.get_recent_logs")
    def test_dashboard_logs(self, mock_logs, client):
        mock_logs.return_value = [
            {"log_id": 1, "action": "INCIDENT_CREATED"},
            {"log_id": 2, "action": "RESOURCES_ALLOCATED"},
        ]
        res = client.get("/api/dashboard/logs?limit=10")
        assert res.status_code == 200
        data = res.get_json()
        assert data["count"] == 2

    def test_dashboard_banker_state(self, client):
        res = client.get("/api/dashboard/banker-state")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert "available" in data["banker_matrices"]
        assert "synchronization" in data

    def test_dashboard_scheduler_status(self, client):
        res = client.get("/api/dashboard/scheduler")
        assert res.status_code == 200
        data = res.get_json()
        assert "stats" in data
        assert "queued_events" in data

    def test_dashboard_worker_stats(self, client):
        res = client.get("/api/dashboard/worker-stats")
        assert res.status_code == 200
        data = res.get_json()
        assert "worker_pool" in data
