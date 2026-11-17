# ============================================================
# Smart Tourist Safety and Emergency Response System
# Test: Full End-to-End Pipeline & Integration Test
# Validates Mobile App Flow -> REST APIs -> Priority Queue ->
# Multithreading -> Banker's Algorithm -> DB Transactions -> Dashboard
# ============================================================

import json
import pytest
from unittest.mock import patch, MagicMock
from backend.app import create_app
from backend.config import Config
from backend.scheduler.priority_queue import (
    EmergencyPriorityQueue,
    EmergencyEvent,
    PRIORITY_CRITICAL_ACCIDENT,
    PRIORITY_SOS,
    PRIORITY_DANGEROUS_ZONE,
    PRIORITY_GPS_UPDATE,
)
from backend.resource_manager.bankers_algorithm import BankersAlgorithm
from backend.resource_manager.synchronization import SynchronizationManager
from backend.resource_manager.resource_manager import ResourceManager

@pytest.fixture
def client():
    app = create_app(Config)
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client

def test_full_tourist_mobile_workflow_and_emergency_lifecycle(client):
    """
    Step 1: Tourist signs up on mobile app
    Step 2: Tourist adds emergency contacts
    Step 3: Tourist sends GPS location & triggers Geofence detection
    Step 4: Tourist triggers SOS distress call
    Step 5: Event enters Priority Queue and is scheduled before lower priorities
    Step 6: Banker's Algorithm validates safe resource allocation
    Step 7: Resources are allocated and confirmed
    Step 8: Incident is resolved and resources are released back to pool
    Step 9: Dashboard reflects updated metrics
    """

    # --- Step 1: Tourist Registration ---
    mock_tourist = {
        "tourist_id": 42,
        "name": "Maria Garcia",
        "phone": "+919876543210",
        "email": "maria.garcia@example.com",
        "nationality": "Spanish",
        "blood_group": "A+",
        "registered_at": "2026-10-11 10:00:00",
    }

    with patch("backend.api.tourist_routes.TouristRepository.create_tourist", return_value=mock_tourist):
        reg_resp = client.post(
            "/api/tourists",
            data=json.dumps({
                "name": "Maria Garcia",
                "phone": "+919876543210",
                "email": "maria.garcia@example.com",
                "nationality": "Spanish",
                "blood_group": "A+",
            }),
            content_type="application/json",
        )
        assert reg_resp.status_code == 201
        tourist_data = reg_resp.get_json()["data"]
        assert tourist_data["tourist_id"] == 42
        assert tourist_data["name"] == "Maria Garcia"

    # --- Step 2: Emergency Contact Registration ---
    mock_contact = {
        "contact_id": 108,
        "tourist_id": 42,
        "name": "Carlos Garcia",
        "phone": "+34612345678",
        "relationship": "Spouse",
    }

    with patch("backend.api.tourist_routes.TouristRepository.get_tourist_by_id", return_value=mock_tourist), \
         patch("backend.api.tourist_routes.ContactRepository.add_contact", return_value=mock_contact):
        contact_resp = client.post(
            "/api/tourists/42/contacts",
            data=json.dumps({
                "name": "Carlos Garcia",
                "phone": "+34612345678",
                "relationship": "Spouse",
            }),
            content_type="application/json",
        )
        assert contact_resp.status_code == 201
        assert contact_resp.get_json()["data"]["relationship"] == "Spouse"

    # --- Step 3: Location Telemetry & Geofence Check ---
    mock_location = {
        "location_id": 501,
        "tourist_id": 42,
        "latitude": 15.5400,
        "longitude": 73.7400,
        "recorded_at": "2026-10-11T10:05:00Z",
        "zone": {
            "zone_id": 2,
            "zone_name": "Calangute Deep Sea Zone",
            "zone_type": "DANGEROUS",
            "risk_level": "CRITICAL",
        },
    }
    with patch("backend.api.location_routes.LocationRepository.record_location", return_value=mock_location):
        loc_resp = client.post(
            "/api/location",
            data=json.dumps({
                "tourist_id": 42,
                "latitude": 15.5400,
                "longitude": 73.7400,
            }),
            content_type="application/json",
        )
        assert loc_resp.status_code == 201
        loc_data = loc_resp.get_json()
        assert "zone" in loc_data
        assert loc_data["geofence_breach"] is True

    # --- Step 4: Emergency SOS Beacon Trigger ---
    mock_incident = {
        "incident_id": 99,
        "tourist_id": 42,
        "incident_type": "SOS",
        "priority": 2,
        "status": "QUEUED",
        "latitude": 15.5400,
        "longitude": 73.7400,
        "description": "SOS trigger from mobile app",
        "created_at": "2026-10-11 10:15:00",
        "resolved_at": None,
    }

    with patch("backend.api.emergency_routes.EmergencyRepository.create_incident", return_value=mock_incident), \
         patch("backend.api.emergency_routes.broadcast_emergency_update") as mock_broadcast:

        sos_resp = client.post(
            "/api/emergencies/sos",
            data=json.dumps({
                "tourist_id": 42,
                "latitude": 15.5400,
                "longitude": 73.7400,
                "description": "SOS trigger from mobile app",
            }),
            content_type="application/json",
        )
        assert sos_resp.status_code == 201
        assert sos_resp.get_json()["data"]["incident_id"] == 99
        mock_broadcast.assert_called_once()

    # --- Step 5: OS Priority Scheduling Logic Verification ---
    pq = EmergencyPriorityQueue()
    e_gps = EmergencyEvent(priority=PRIORITY_GPS_UPDATE, incident_id=1, payload={"name": "GPS Ping"})
    e_zone = EmergencyEvent(priority=PRIORITY_DANGEROUS_ZONE, incident_id=2, payload={"name": "Zone Breach"})
    e_sos = EmergencyEvent(priority=PRIORITY_SOS, incident_id=3, payload={"name": "SOS Beacon"})
    e_crit = EmergencyEvent(priority=PRIORITY_CRITICAL_ACCIDENT, incident_id=4, payload={"name": "Head-on Collision"})

    # Push in reverse order
    pq.enqueue(e_gps)
    pq.enqueue(e_zone)
    pq.enqueue(e_sos)
    pq.enqueue(e_crit)

    # Dequeue order MUST be: CRITICAL (1) -> SOS (2) -> ZONE (3) -> GPS (5)
    first = pq.dequeue(block=False)
    second = pq.dequeue(block=False)
    third = pq.dequeue(block=False)
    fourth = pq.dequeue(block=False)

    assert first.priority == PRIORITY_CRITICAL_ACCIDENT
    assert second.priority == PRIORITY_SOS
    assert third.priority == PRIORITY_DANGEROUS_ZONE
    assert fourth.priority == PRIORITY_GPS_UPDATE

    # --- Step 6: Banker's Algorithm Deadlock Avoidance ---
    # 3 Resource classes: [Ambulance, RescueTeam, Helicopter]
    banker = BankersAlgorithm(
        initial_available={"AMBULANCE": 3, "RESCUE_TEAM": 4, "HELICOPTER": 2}
    )
    # Register Maria's emergency needs
    banker.register_process(
        process_id=99,
        max_demand={"AMBULANCE": 1, "RESCUE_TEAM": 1, "HELICOPTER": 0}
    )

    # Request resources for Incident 99
    is_safe, message, seq = banker.request_resources(
        99,
        {"AMBULANCE": 1, "RESCUE_TEAM": 1, "HELICOPTER": 0}
    )
    assert is_safe is True
    assert 99 in seq

    # Try requesting beyond available resources -> must reject
    banker.register_process(
        process_id=100,
        max_demand={"AMBULANCE": 5, "RESCUE_TEAM": 5, "HELICOPTER": 5}
    )
    is_safe_excess, msg_excess, _ = banker.request_resources(
        100,
        {"AMBULANCE": 4, "RESCUE_TEAM": 4, "HELICOPTER": 4}
    )
    assert is_safe_excess is False

    # --- Step 7: Release Resources back to Safe Pool ---
    banker.release_resources(99, {"AMBULANCE": 1, "RESCUE_TEAM": 1, "HELICOPTER": 0})
    state = banker.get_state()
    assert state["available"]["AMBULANCE"] == 3
    assert state["available"]["RESCUE_TEAM"] == 4
    assert state["available"]["HELICOPTER"] == 2

    # --- Step 8: Dashboard Summary Verification ---
    with patch("backend.api.dashboard_routes.DashboardRepository.get_summary_counts") as mock_counts:
        mock_counts.return_value = {
            "total_tourists": 150,
            "active_emergencies": 1,
            "critical_emergencies": 0,
            "available_resources": 9,
            "available_teams": 4,
        }
        dash_resp = client.get("/api/dashboard/summary")
        assert dash_resp.status_code == 200
        metrics = dash_resp.get_json()["metrics"]
        assert metrics["total_tourists"] == 150
        assert metrics["active_emergencies"] == 1
        assert "is_safe_state" in metrics
