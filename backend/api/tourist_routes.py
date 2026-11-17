# ============================================================
# Smart Tourist Safety and Emergency Response System
# Tourist Management API Routes (Phase 7)
# ============================================================

from flask import Blueprint, jsonify, request
from backend.db.repositories import (
    TouristRepository,
    ContactRepository,
    LocationRepository,
    DuplicateRecordError,
    RecordNotFoundError,
    DependencyConflictError,
)
from backend.utils.validators import validate_tourist_data, validate_contact_data
from backend.utils.logger import logger

tourist_bp = Blueprint("tourists", __name__)

@tourist_bp.route("/ping", methods=["GET"])
def ping_tourists():
    """Diagnostic ping endpoint for Tourist blueprint."""
    return jsonify({
        "module": "tourists",
        "status": "active",
        "message": "Tourist API blueprint operational"
    }), 200

@tourist_bp.route("", methods=["POST"])
def register_tourist():
    """Registers a new tourist in the system."""
    data = request.get_json(silent=True)
    is_valid, errors = validate_tourist_data(data, is_update=False)
    if not is_valid:
        return jsonify({
            "error": "Validation Error",
            "message": "Invalid tourist registration payload",
            "errors": errors,
            "status_code": 400
        }), 400

    try:
        tourist = TouristRepository.create_tourist(
            name=data["name"],
            phone=data["phone"],
            email=data["email"],
            nationality=data.get("nationality"),
            blood_group=data.get("blood_group"),
        )
        return jsonify({
            "status": "success",
            "message": "Tourist registered successfully",
            "data": tourist
        }), 201
    except DuplicateRecordError as e:
        return jsonify({
            "error": "Conflict",
            "message": str(e),
            "status_code": 409
        }), 409
    except Exception as e:
        logger.error(f"Unexpected error in register_tourist: {e}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "Could not register tourist due to a database error.",
            "status_code": 500
        }), 500

@tourist_bp.route("", methods=["GET"])
def list_tourists():
    """Returns a list of all registered tourists with emergency contact counts."""
    limit = request.args.get("limit", default=50, type=int)
    offset = request.args.get("offset", default=0, type=int)
    
    # Cap limit to 100 for safety
    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    try:
        tourists = TouristRepository.get_tourists(limit=limit, offset=offset)
        return jsonify({
            "status": "success",
            "count": len(tourists),
            "limit": limit,
            "offset": offset,
            "data": tourists
        }), 200
    except Exception as e:
        logger.error(f"Error fetching tourists: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve tourists.",
            "status_code": 500
        }), 500

@tourist_bp.route("/<int:tourist_id>", methods=["GET"])
def get_tourist(tourist_id: int):
    """Retrieves full profile for a specific tourist, including emergency contacts."""
    try:
        tourist = TouristRepository.get_tourist_by_id(tourist_id)
        if not tourist:
            return jsonify({
                "error": "Not Found",
                "message": f"Tourist #{tourist_id} does not exist.",
                "status_code": 404
            }), 404

        return jsonify({
            "status": "success",
            "data": tourist
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving tourist #{tourist_id}: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve tourist profile.",
            "status_code": 500
        }), 500

@tourist_bp.route("/<int:tourist_id>", methods=["PUT"])
def update_tourist(tourist_id: int):
    """Updates fields of an existing tourist profile."""
    data = request.get_json(silent=True)
    is_valid, errors = validate_tourist_data(data, is_update=True)
    if not is_valid:
        return jsonify({
            "error": "Validation Error",
            "message": "Invalid tourist update payload",
            "errors": errors,
            "status_code": 400
        }), 400

    try:
        existing = TouristRepository.get_tourist_by_id(tourist_id)
        if not existing:
            return jsonify({
                "error": "Not Found",
                "message": f"Tourist #{tourist_id} does not exist.",
                "status_code": 404
            }), 404

        updated = TouristRepository.update_tourist(tourist_id, **data)
        return jsonify({
            "status": "success",
            "message": f"Tourist #{tourist_id} updated successfully.",
            "data": updated
        }), 200
    except DuplicateRecordError as e:
        return jsonify({
            "error": "Conflict",
            "message": str(e),
            "status_code": 409
        }), 409
    except Exception as e:
        logger.error(f"Error updating tourist #{tourist_id}: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not update tourist profile.",
            "status_code": 500
        }), 500

@tourist_bp.route("/<int:tourist_id>", methods=["DELETE"])
def delete_tourist(tourist_id: int):
    """Deletes a tourist profile (blocked if active incidents exist)."""
    try:
        existing = TouristRepository.get_tourist_by_id(tourist_id)
        if not existing:
            return jsonify({
                "error": "Not Found",
                "message": f"Tourist #{tourist_id} does not exist.",
                "status_code": 404
            }), 404

        deleted = TouristRepository.delete_tourist(tourist_id)
        if deleted:
            return jsonify({
                "status": "success",
                "message": f"Tourist #{tourist_id} and related personal contacts deleted successfully."
            }), 200
        return jsonify({
            "error": "Not Found",
            "message": f"Tourist #{tourist_id} could not be deleted.",
            "status_code": 404
        }), 404
    except DependencyConflictError as e:
        return jsonify({
            "error": "Conflict",
            "message": str(e),
            "status_code": 409
        }), 409
    except Exception as e:
        logger.error(f"Error deleting tourist #{tourist_id}: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not delete tourist profile.",
            "status_code": 500
        }), 500

# ============================================================
# Emergency Contacts Endpoints
# ============================================================

@tourist_bp.route("/<int:tourist_id>/contacts", methods=["POST"])
def add_contact(tourist_id: int):
    """Adds a new emergency contact for a tourist."""
    data = request.get_json(silent=True)
    is_valid, errors = validate_contact_data(data)
    if not is_valid:
        return jsonify({
            "error": "Validation Error",
            "message": "Invalid emergency contact payload",
            "errors": errors,
            "status_code": 400
        }), 400

    try:
        contact = ContactRepository.add_contact(
            tourist_id=tourist_id,
            name=data["name"],
            phone=data["phone"],
            relationship=data["relationship"],
        )
        return jsonify({
            "status": "success",
            "message": "Emergency contact added successfully.",
            "data": contact
        }), 201
    except RecordNotFoundError as e:
        return jsonify({
            "error": "Not Found",
            "message": str(e),
            "status_code": 404
        }), 404
    except Exception as e:
        logger.error(f"Error adding contact for tourist #{tourist_id}: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not add emergency contact.",
            "status_code": 500
        }), 500

@tourist_bp.route("/<int:tourist_id>/contacts", methods=["GET"])
def get_contacts(tourist_id: int):
    """Retrieves all emergency contacts for a tourist."""
    try:
        tourist = TouristRepository.get_tourist_by_id(tourist_id)
        if not tourist:
            return jsonify({
                "error": "Not Found",
                "message": f"Tourist #{tourist_id} does not exist.",
                "status_code": 404
            }), 404

        contacts = ContactRepository.get_contacts(tourist_id)
        return jsonify({
            "status": "success",
            "tourist_id": tourist_id,
            "count": len(contacts),
            "data": contacts
        }), 200
    except Exception as e:
        logger.error(f"Error fetching contacts for tourist #{tourist_id}: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve emergency contacts.",
            "status_code": 500
        }), 500

@tourist_bp.route("/<int:tourist_id>/contacts/<int:contact_id>", methods=["DELETE"])
def delete_contact(tourist_id: int, contact_id: int):
    """Deletes an emergency contact."""
    try:
        deleted = ContactRepository.delete_contact(tourist_id, contact_id)
        if not deleted:
            return jsonify({
                "error": "Not Found",
                "message": f"Contact #{contact_id} not found for tourist #{tourist_id}.",
                "status_code": 404
            }), 404

        return jsonify({
            "status": "success",
            "message": f"Contact #{contact_id} deleted successfully."
        }), 200
    except Exception as e:
        logger.error(f"Error deleting contact #{contact_id}: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not delete emergency contact.",
            "status_code": 500
        }), 500

@tourist_bp.route("/<int:tourist_id>/locations", methods=["GET"])
def get_tourist_locations(tourist_id: int):
    """Retrieves paginated location history for a tourist (cross-referenced under /api/tourists)."""
    limit = request.args.get("limit", default=50, type=int)
    offset = request.args.get("offset", default=0, type=int)

    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    try:
        history = LocationRepository.get_location_history(
            tourist_id=tourist_id,
            limit=limit,
            offset=offset
        )
        return jsonify({
            "status": "success",
            "tourist_id": tourist_id,
            "count": len(history),
            "limit": limit,
            "offset": offset,
            "data": history
        }), 200
    except RecordNotFoundError as e:
        return jsonify({
            "error": "Not Found",
            "message": str(e),
            "status_code": 404
        }), 404
    except Exception as e:
        logger.error(f"Error fetching locations for tourist #{tourist_id}: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve location history.",
            "status_code": 500
        }), 500
