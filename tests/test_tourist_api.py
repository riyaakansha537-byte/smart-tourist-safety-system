# ============================================================
# Smart Tourist Safety and Emergency Response System
# Tests: Tourist & Contact APIs (Phase 7)
# ============================================================

from unittest.mock import patch
import pytest
from backend.app import create_app
from backend.config import Config
from backend.db.repositories import (
    DuplicateRecordError,
    RecordNotFoundError,
    DependencyConflictError,
)
from backend.utils.validators import validate_tourist_data, validate_contact_data

class TestValidators:
    """Tests payload validation logic for tourists and contacts."""

    def test_validate_tourist_valid(self):
        payload = {
            "name": "Alice Johnson",
            "phone": "+1-555-0101",
            "email": "alice@example.com",
            "nationality": "American",
            "blood_group": "O+",
        }
        is_valid, errors = validate_tourist_data(payload)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_tourist_missing_required(self):
        is_valid, errors = validate_tourist_data({})
        assert is_valid is False
        assert any("name" in e for e in errors)
        assert any("phone" in e for e in errors)
        assert any("email" in e for e in errors)

    def test_validate_tourist_invalid_blood_group(self):
        payload = {
            "name": "Bob",
            "phone": "+1-555-0102",
            "email": "bob@example.com",
            "blood_group": "XYZ",
        }
        is_valid, errors = validate_tourist_data(payload)
        assert is_valid is False
        assert any("blood_group" in e for e in errors)

    def test_validate_contact_valid(self):
        payload = {
            "name": "Jane Doe",
            "phone": "+1-555-0103",
            "relationship": "Spouse",
        }
        is_valid, errors = validate_contact_data(payload)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_contact_missing_fields(self):
        is_valid, errors = validate_contact_data({"name": ""})
        assert is_valid is False
        assert len(errors) >= 2

class TestTouristAPI:
    """Tests Tourist and Emergency Contact REST API endpoints."""

    @pytest.fixture
    def client(self):
        app = create_app(Config)
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    @patch("backend.api.tourist_routes.TouristRepository.create_tourist")
    def test_register_tourist_success(self, mock_create, client):
        mock_create.return_value = {
            "tourist_id": 1,
            "name": "Alice Johnson",
            "phone": "+1-555-0101",
            "email": "alice@example.com",
            "nationality": "American",
            "blood_group": "O+",
            "registered_at": "2026-10-03T12:00:00Z",
        }
        payload = {
            "name": "Alice Johnson",
            "phone": "+1-555-0101",
            "email": "alice@example.com",
            "nationality": "American",
            "blood_group": "O+",
        }
        res = client.post("/api/tourists", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["status"] == "success"
        assert data["data"]["tourist_id"] == 1

    def test_register_tourist_validation_error(self, client):
        res = client.post("/api/tourists", json={"name": "A"})
        assert res.status_code == 400
        data = res.get_json()
        assert data["error"] == "Validation Error"
        assert len(data["errors"]) >= 2

    @patch("backend.api.tourist_routes.TouristRepository.create_tourist")
    def test_register_tourist_duplicate_conflict(self, mock_create, client):
        mock_create.side_effect = DuplicateRecordError("Tourist already exists.")
        payload = {
            "name": "Alice Johnson",
            "phone": "+1-555-0101",
            "email": "alice@example.com",
        }
        res = client.post("/api/tourists", json=payload)
        assert res.status_code == 409
        data = res.get_json()
        assert data["error"] == "Conflict"

    @patch("backend.api.tourist_routes.TouristRepository.get_tourists")
    def test_list_tourists(self, mock_get_all, client):
        mock_get_all.return_value = [
            {"tourist_id": 1, "name": "Alice", "contact_count": 2},
            {"tourist_id": 2, "name": "Bob", "contact_count": 0},
        ]
        res = client.get("/api/tourists?limit=10&offset=0")
        assert res.status_code == 200
        data = res.get_json()
        assert data["count"] == 2
        assert len(data["data"]) == 2

    @patch("backend.api.tourist_routes.TouristRepository.get_tourist_by_id")
    def test_get_tourist_by_id_found(self, mock_get_id, client):
        mock_get_id.return_value = {
            "tourist_id": 1,
            "name": "Alice",
            "emergency_contacts": [{"contact_id": 1, "name": "Robert"}],
        }
        res = client.get("/api/tourists/1")
        assert res.status_code == 200
        data = res.get_json()
        assert data["data"]["name"] == "Alice"

    @patch("backend.api.tourist_routes.TouristRepository.get_tourist_by_id")
    def test_get_tourist_by_id_not_found(self, mock_get_id, client):
        mock_get_id.return_value = None
        res = client.get("/api/tourists/999")
        assert res.status_code == 404
        data = res.get_json()
        assert data["error"] == "Not Found"

    @patch("backend.api.tourist_routes.TouristRepository.get_tourist_by_id")
    @patch("backend.api.tourist_routes.TouristRepository.update_tourist")
    def test_update_tourist_success(self, mock_update, mock_get_id, client):
        mock_get_id.return_value = {"tourist_id": 1, "name": "Alice"}
        mock_update.return_value = {"tourist_id": 1, "name": "Alice Smith"}

        res = client.put("/api/tourists/1", json={"name": "Alice Smith"})
        assert res.status_code == 200
        data = res.get_json()
        assert data["data"]["name"] == "Alice Smith"

    @patch("backend.api.tourist_routes.TouristRepository.get_tourist_by_id")
    @patch("backend.api.tourist_routes.TouristRepository.delete_tourist")
    def test_delete_tourist_success(self, mock_del, mock_get_id, client):
        mock_get_id.return_value = {"tourist_id": 1}
        mock_del.return_value = True

        res = client.delete("/api/tourists/1")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"

    @patch("backend.api.tourist_routes.TouristRepository.get_tourist_by_id")
    @patch("backend.api.tourist_routes.TouristRepository.delete_tourist")
    def test_delete_tourist_conflict(self, mock_del, mock_get_id, client):
        mock_get_id.return_value = {"tourist_id": 1}
        mock_del.side_effect = DependencyConflictError("Cannot delete: active incidents exist.")

        res = client.delete("/api/tourists/1")
        assert res.status_code == 409
        data = res.get_json()
        assert data["error"] == "Conflict"

    @patch("backend.api.tourist_routes.ContactRepository.add_contact")
    def test_add_emergency_contact_success(self, mock_add_c, client):
        mock_add_c.return_value = {
            "contact_id": 10,
            "tourist_id": 1,
            "name": "Jane",
            "phone": "+1-555-9999",
            "relationship": "Spouse",
        }
        payload = {"name": "Jane", "phone": "+1-555-9999", "relationship": "Spouse"}
        res = client.post("/api/tourists/1/contacts", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["data"]["contact_id"] == 10

    @patch("backend.api.tourist_routes.TouristRepository.get_tourist_by_id")
    @patch("backend.api.tourist_routes.ContactRepository.get_contacts")
    def test_get_emergency_contacts_success(self, mock_get_c, mock_get_t, client):
        mock_get_t.return_value = {"tourist_id": 1}
        mock_get_c.return_value = [
            {"contact_id": 10, "name": "Jane", "relationship": "Spouse"}
        ]
        res = client.get("/api/tourists/1/contacts")
        assert res.status_code == 200
        data = res.get_json()
        assert data["count"] == 1

    @patch("backend.api.tourist_routes.ContactRepository.delete_contact")
    def test_delete_emergency_contact_success(self, mock_del_c, client):
        mock_del_c.return_value = True
        res = client.delete("/api/tourists/1/contacts/10")
        assert res.status_code == 200
