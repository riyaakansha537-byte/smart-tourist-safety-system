# ============================================================
# Smart Tourist Safety and Emergency Response System
# Tests: Location Tracking, Geofencing & API (Phase 8)
# ============================================================

from unittest.mock import patch
import pytest
from backend.app import create_app
from backend.config import Config
from backend.db.repositories import RecordNotFoundError
from backend.utils.geofence import (
    haversine_distance_km,
    is_point_in_zone,
    detect_primary_zone,
)
from backend.utils.validators import validate_location_data

class TestGeofenceUtils:
    """Tests spatial distance calculation and geofence zone detection logic."""

    def test_haversine_distance_zero(self):
        # Same coordinate should have 0 distance
        d = haversine_distance_km(15.5553, 73.7516, 15.5553, 73.7516)
        assert d == 0.0

    def test_haversine_distance_known_points(self):
        # Distance between Baga Beach (15.5553, 73.7516) and Aguada (15.4925, 73.7735) is ~7.3 km
        d = haversine_distance_km(15.5553, 73.7516, 15.4925, 73.7735)
        assert 6.0 <= d <= 8.5

    def test_is_point_in_zone_inside(self):
        zone = {
            "zone_id": 1,
            "zone_name": "Baga Beach Promenade",
            "center_lat": 15.5553,
            "center_lng": 73.7516,
            "radius_km": 2.5,
        }
        # Point 0.5 km away from center
        inside, dist = is_point_in_zone(15.5580, 73.7530, zone)
        assert inside is True
        assert dist < 2.5

    def test_is_point_in_zone_outside(self):
        zone = {
            "zone_id": 1,
            "zone_name": "Baga Beach Promenade",
            "center_lat": 15.5553,
            "center_lng": 73.7516,
            "radius_km": 2.5,
        }
        # Far coordinate
        inside, dist = is_point_in_zone(15.0872, 74.2081, zone)
        assert inside is False
        assert dist > 2.5

    def test_detect_primary_zone_prioritizes_dangerous_over_safe(self):
        zones = [
            {
                "zone_id": 1,
                "zone_name": "Safe Haven",
                "zone_type": "SAFE",
                "center_lat": 15.5000,
                "center_lng": 73.8000,
                "radius_km": 5.0,
                "risk_level": "LOW",
            },
            {
                "zone_id": 2,
                "zone_name": "Hazardous Reef",
                "zone_type": "DANGEROUS",
                "center_lat": 15.5010,
                "center_lng": 73.8010,
                "radius_km": 3.0,
                "risk_level": "HIGH",
            },
        ]
        # Point inside both zones
        primary = detect_primary_zone(15.5005, 73.8005, zones)
        assert primary is not None
        assert primary["zone_id"] == 2
        assert primary["zone_type"] == "DANGEROUS"

    def test_detect_primary_zone_none_outside_all(self):
        zones = [
            {
                "zone_id": 1,
                "zone_name": "Safe Haven",
                "zone_type": "SAFE",
                "center_lat": 15.5000,
                "center_lng": 73.8000,
                "radius_km": 1.0,
                "risk_level": "LOW",
            }
        ]
        # Point far away
        primary = detect_primary_zone(16.5000, 75.8000, zones)
        assert primary is None

class TestLocationValidators:
    """Tests location telemetry validation logic."""

    def test_validate_location_valid(self):
        payload = {
            "tourist_id": 1,
            "latitude": 15.5553,
            "longitude": 73.7516,
        }
        is_valid, errors = validate_location_data(payload)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_location_missing_fields(self):
        is_valid, errors = validate_location_data({})
        assert is_valid is False
        assert any("tourist_id" in e for e in errors)
        assert any("latitude" in e for e in errors)
        assert any("longitude" in e for e in errors)

    def test_validate_location_invalid_coords(self):
        payload = {
            "tourist_id": 1,
            "latitude": 105.0,  # invalid lat (> 90)
            "longitude": -200.0,  # invalid lon (< -180)
        }
        is_valid, errors = validate_location_data(payload)
        assert is_valid is False
        assert any("latitude" in e for e in errors)
        assert any("longitude" in e for e in errors)

    def test_validate_location_invalid_types(self):
        payload = {
            "tourist_id": "one",
            "latitude": "north",
            "longitude": False,
        }
        is_valid, errors = validate_location_data(payload)
        assert is_valid is False

class TestLocationAPI:
    """Tests Location REST API endpoints."""

    @pytest.fixture
    def client(self):
        app = create_app(Config)
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_ping_location(self, client):
        res = client.get("/api/location/ping")
        assert res.status_code == 200
        data = res.get_json()
        assert data["module"] == "location"
        assert data["status"] == "active"

    @patch("backend.api.location_routes.LocationRepository.record_location")
    def test_submit_location_safe_zone(self, mock_record, client):
        mock_record.return_value = {
            "location_id": 101,
            "tourist_id": 1,
            "latitude": 15.5553,
            "longitude": 73.7516,
            "recorded_at": "2026-10-03T14:00:00Z",
            "zone_id": 1,
            "zone": {
                "zone_id": 1,
                "zone_name": "Baga Beach Promenade",
                "zone_type": "SAFE",
                "risk_level": "LOW",
            },
        }
        payload = {"tourist_id": 1, "latitude": 15.5553, "longitude": 73.7516}
        res = client.post("/api/location", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["status"] == "success"
        assert data["data"]["location_id"] == 101
        assert data["geofence_breach"] is False
        assert data["warning"] is None

    @patch("backend.api.location_routes.LocationRepository.record_location")
    def test_submit_location_dangerous_zone_alert(self, mock_record, client):
        mock_record.return_value = {
            "location_id": 102,
            "tourist_id": 2,
            "latitude": 15.4925,
            "longitude": 73.7735,
            "recorded_at": "2026-10-03T14:05:00Z",
            "zone_id": 5,
            "zone": {
                "zone_id": 5,
                "zone_name": "Aguada Sea Cliff & Surge Area",
                "zone_type": "DANGEROUS",
                "risk_level": "HIGH",
            },
        }
        payload = {"tourist_id": 2, "latitude": 15.4925, "longitude": 73.7735}
        res = client.post("/api/location", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["status"] == "success"
        assert data["geofence_breach"] is True
        assert "DANGEROUS" in data["warning"]
        assert "Aguada Sea Cliff" in data["warning"]

    def test_submit_location_validation_error(self, client):
        res = client.post("/api/location", json={"tourist_id": -1})
        assert res.status_code == 400
        data = res.get_json()
        assert data["error"] == "Validation Error"

    @patch("backend.api.location_routes.LocationRepository.record_location")
    def test_submit_location_tourist_not_found(self, mock_record, client):
        mock_record.side_effect = RecordNotFoundError("Tourist with ID 999 does not exist.")
        payload = {"tourist_id": 999, "latitude": 15.5553, "longitude": 73.7516}
        res = client.post("/api/location", json=payload)
        assert res.status_code == 404
        data = res.get_json()
        assert data["error"] == "Not Found"

    @patch("backend.api.location_routes.ZoneRepository.get_active_zones")
    def test_get_active_zones(self, mock_zones, client):
        mock_zones.return_value = [
            {"zone_id": 1, "zone_name": "Baga Beach", "zone_type": "SAFE"},
            {"zone_id": 2, "zone_name": "Aguada Sea Cliff", "zone_type": "DANGEROUS"},
        ]
        res = client.get("/api/location/zones")
        assert res.status_code == 200
        data = res.get_json()
        assert data["count"] == 2
        assert len(data["data"]) == 2

    @patch("backend.api.location_routes.LocationRepository.get_location_history")
    def test_get_tourist_location_history(self, mock_history, client):
        mock_history.return_value = [
            {"location_id": 2, "tourist_id": 1, "latitude": 15.55, "longitude": 73.75},
            {"location_id": 1, "tourist_id": 1, "latitude": 15.54, "longitude": 73.74},
        ]
        res = client.get("/api/location/1?limit=10&offset=0")
        assert res.status_code == 200
        data = res.get_json()
        assert data["count"] == 2
        assert data["tourist_id"] == 1

    @patch("backend.api.location_routes.LocationRepository.get_latest_location")
    def test_get_latest_location_found(self, mock_latest, client):
        mock_latest.return_value = {
            "location_id": 105,
            "tourist_id": 1,
            "latitude": 15.5553,
            "longitude": 73.7516,
            "zone": None,
        }
        res = client.get("/api/location/1/latest")
        assert res.status_code == 200
        data = res.get_json()
        assert data["data"]["location_id"] == 105

    @patch("backend.api.location_routes.LocationRepository.get_latest_location")
    def test_get_latest_location_not_found(self, mock_latest, client):
        mock_latest.return_value = None
        res = client.get("/api/location/1/latest")
        assert res.status_code == 404

    @patch("backend.api.tourist_routes.LocationRepository.get_location_history")
    def test_get_tourist_locations_via_tourist_bp(self, mock_history, client):
        mock_history.return_value = [
            {"location_id": 10, "tourist_id": 1, "latitude": 15.5, "longitude": 73.7}
        ]
        res = client.get("/api/tourists/1/locations")
        assert res.status_code == 200
        data = res.get_json()
        assert data["count"] == 1
