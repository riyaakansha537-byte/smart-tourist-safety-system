# ============================================================
# Smart Tourist Safety and Emergency Response System
# Location Tracking & Geofencing API Routes (Phase 8)
# ============================================================

from flask import Blueprint, jsonify, request
from backend.db.repositories import (
    LocationRepository,
    ZoneRepository,
    RecordNotFoundError,
)
from backend.utils.validators import validate_location_data
from backend.utils.logger import logger

location_bp = Blueprint("location", __name__)

@location_bp.route("/ping", methods=["GET"])
def ping_location():
    """Diagnostic ping endpoint for Location blueprint."""
    return jsonify({
        "module": "location",
        "status": "active",
        "message": "Location telemetry API blueprint operational"
    }), 200

@location_bp.route("", methods=["POST"], strict_slashes=False)
def submit_location():
    """
    Submits GPS telemetry for a tourist.
    Automatically calculates geofence boundaries against active zones.
    If entering a dangerous zone, triggers a safety alert in the response.
    """
    data = request.get_json(silent=True)
    is_valid, errors = validate_location_data(data)
    if not is_valid:
        return jsonify({
            "error": "Validation Error",
            "message": "Invalid location telemetry payload",
            "errors": errors,
            "status_code": 400
        }), 400

    try:
        tourist_id = int(data["tourist_id"])
        latitude = float(data["latitude"])
        longitude = float(data["longitude"])
        zone_id = data.get("zone_id")
        if zone_id is not None:
            zone_id = int(zone_id)

        location = LocationRepository.record_location(
            tourist_id=tourist_id,
            latitude=latitude,
            longitude=longitude,
            zone_id=zone_id
        )

        warning = None
        zone_info = location.get("zone")
        if zone_info and zone_info.get("zone_type") == "DANGEROUS":
            warning = (
                f"ALERT: Tourist has entered a DANGEROUS zone: {zone_info['zone_name']} "
                f"(Risk: {zone_info['risk_level']})"
            )
            logger.warning(
                f"Geofence breach detected! Tourist #{tourist_id} in {zone_info['zone_name']} "
                f"({zone_info['risk_level']})"
            )

        response_payload = {
            "status": "success",
            "message": "Location telemetry recorded successfully",
            "data": location,
            "zone": zone_info,
            "warning": warning,
            "geofence_breach": bool(warning)
        }
        return jsonify(response_payload), 201

    except RecordNotFoundError as e:
        return jsonify({
            "error": "Not Found",
            "message": str(e),
            "status_code": 404
        }), 404
    except Exception as e:
        logger.error(f"Unexpected error in submit_location: {e}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "Could not record location telemetry due to a database error.",
            "status_code": 500
        }), 500

@location_bp.route("/zones", methods=["GET"])
def get_zones():
    """Returns all currently active safe and dangerous zones."""
    try:
        zones = ZoneRepository.get_active_zones()
        return jsonify({
            "status": "success",
            "count": len(zones),
            "data": zones
        }), 200
    except Exception as e:
        logger.error(f"Error fetching zones: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve geofence zones.",
            "status_code": 500
        }), 500

@location_bp.route("/<int:tourist_id>", methods=["GET"])
def get_tourist_location_history(tourist_id: int):
    """Retrieves paginated location history for a specific tourist."""
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
        logger.error(f"Error fetching location history for tourist #{tourist_id}: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve location history.",
            "status_code": 500
        }), 500

@location_bp.route("/<int:tourist_id>/latest", methods=["GET"])
def get_tourist_latest_location(tourist_id: int):
    """Retrieves the single latest recorded location for a specific tourist."""
    try:
        location = LocationRepository.get_latest_location(tourist_id)
        if not location:
            return jsonify({
                "error": "Not Found",
                "message": f"No location records found for tourist #{tourist_id}.",
                "status_code": 404
            }), 404

        return jsonify({
            "status": "success",
            "data": location
        }), 200
    except RecordNotFoundError as e:
        return jsonify({
            "error": "Not Found",
            "message": str(e),
            "status_code": 404
        }), 404
    except Exception as e:
        logger.error(f"Error fetching latest location for tourist #{tourist_id}: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve latest location.",
            "status_code": 500
        }), 500
