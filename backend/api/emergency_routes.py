# ============================================================
# Smart Tourist Safety and Emergency Response System
# Emergency & SOS Management API Routes (Phase 9)
# ============================================================

from flask import Blueprint, jsonify, request
from backend.db.repositories import (
    EmergencyRepository,
    RecordNotFoundError,
)
from backend.utils.validators import (
    validate_emergency_data,
    validate_status_update_data,
)
from backend.notifications.socket_service import broadcast_emergency_update
from backend.utils.logger import logger

emergency_bp = Blueprint("emergencies", __name__)

@emergency_bp.route("/ping", methods=["GET"])
def ping_emergencies():
    """Diagnostic ping endpoint for Emergency blueprint."""
    return jsonify({
        "module": "emergencies",
        "status": "active",
        "message": "Emergency dispatch API blueprint operational"
    }), 200

def _handle_create_emergency(default_type: str, default_priority: int):
    """Helper function to validate, persist, and broadcast an emergency report."""
    data = request.get_json(silent=True)
    is_valid, errors = validate_emergency_data(
        data,
        default_type=default_type,
        default_priority=default_priority
    )
    if not is_valid:
        return jsonify({
            "error": "Validation Error",
            "message": "Invalid emergency report payload",
            "errors": errors,
            "status_code": 400
        }), 400

    try:
        tourist_id = int(data["tourist_id"])
        latitude = float(data["latitude"])
        longitude = float(data["longitude"])
        incident_type = data.get("incident_type", default_type)
        priority = int(data.get("priority", default_priority))
        description = data.get("description")

        incident = EmergencyRepository.create_incident(
            tourist_id=tourist_id,
            incident_type=incident_type,
            priority=priority,
            latitude=latitude,
            longitude=longitude,
            description=description,
            status="RECEIVED"
        )

        # Notify active dispatchers and monitoring dashboards in real-time
        try:
            broadcast_emergency_update(
                event_type="emergency_alert",
                payload={"event": "NEW_EMERGENCY", "incident": incident}
            )
        except Exception as ws_err:
            logger.warning(f"Could not broadcast Socket.IO emergency update: {ws_err}")

        return jsonify({
            "status": "success",
            "message": f"Emergency incident [{incident_type}] registered with Priority {priority}",
            "data": incident
        }), 201

    except RecordNotFoundError as e:
        return jsonify({
            "error": "Not Found",
            "message": str(e),
            "status_code": 404
        }), 404
    except Exception as e:
        logger.error(f"Error creating emergency incident: {e}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "Could not register emergency incident due to a database error.",
            "status_code": 500
        }), 500

@emergency_bp.route("/accident", methods=["POST"])
def report_critical_accident():
    """Reports a critical accident (Priority 1: Immediate dispatch)."""
    return _handle_create_emergency("CRITICAL_ACCIDENT", 1)

@emergency_bp.route("/sos", methods=["POST"])
def report_sos():
    """Reports an SOS distress signal triggered by a tourist (Priority 2)."""
    return _handle_create_emergency("SOS", 2)

@emergency_bp.route("/geofence", methods=["POST"])
def report_geofence_breach():
    """Reports entry into a dangerous geofence zone (Priority 3)."""
    return _handle_create_emergency("DANGEROUS_ZONE", 3)

@emergency_bp.route("/safety-alert", methods=["POST"])
def report_safety_alert():
    """Reports a general safety concern or precautionary alert (Priority 4)."""
    return _handle_create_emergency("SAFETY_ALERT", 4)

@emergency_bp.route("", methods=["POST"])
def create_emergency():
    """General emergency reporting endpoint allowing custom incident_type and priority."""
    return _handle_create_emergency("SAFETY_ALERT", 4)

@emergency_bp.route("", methods=["GET"])
def list_emergencies():
    """Returns a filtered, paginated list of emergency incidents ordered by priority."""
    status = request.args.get("status")
    incident_type = request.args.get("incident_type")
    priority = request.args.get("priority", type=int)
    limit = request.args.get("limit", default=50, type=int)
    offset = request.args.get("offset", default=0, type=int)

    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    try:
        incidents = EmergencyRepository.get_incidents(
            status=status,
            incident_type=incident_type,
            priority=priority,
            limit=limit,
            offset=offset
        )
        return jsonify({
            "status": "success",
            "count": len(incidents),
            "limit": limit,
            "offset": offset,
            "data": incidents
        }), 200
    except Exception as e:
        logger.error(f"Error fetching emergency incidents: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve emergency incidents.",
            "status_code": 500
        }), 500

@emergency_bp.route("/<int:incident_id>", methods=["GET"])
def get_emergency(incident_id: int):
    """Retrieves full details for an emergency incident, including its complete audit trail."""
    try:
        incident = EmergencyRepository.get_incident_by_id(incident_id)
        if not incident:
            return jsonify({
                "error": "Not Found",
                "message": f"Emergency incident #{incident_id} not found.",
                "status_code": 404
            }), 404

        return jsonify({
            "status": "success",
            "data": incident
        }), 200
    except Exception as e:
        logger.error(f"Error fetching emergency incident #{incident_id}: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve emergency incident.",
            "status_code": 500
        }), 500

@emergency_bp.route("/<int:incident_id>/status", methods=["PATCH"])
def update_emergency_status(incident_id: int):
    """Updates the status of an emergency incident and appends an immutable audit log."""
    data = request.get_json(silent=True)
    is_valid, errors = validate_status_update_data(data)
    if not is_valid:
        return jsonify({
            "error": "Validation Error",
            "message": "Invalid status update payload",
            "errors": errors,
            "status_code": 400
        }), 400

    new_status = data["status"].strip().upper()
    action = data.get("action", f"STATUS_CHANGED_TO_{new_status}")
    details = data.get("details", f"Incident status transitioned to {new_status}.")
    performed_by = data.get("performed_by", "OPERATOR")

    try:
        updated = EmergencyRepository.update_incident_status(
            incident_id=incident_id,
            status=new_status,
            action=action,
            details=details,
            performed_by=performed_by
        )
        if not updated:
            return jsonify({
                "error": "Not Found",
                "message": f"Emergency incident #{incident_id} not found.",
                "status_code": 404
            }), 404

        try:
            broadcast_emergency_update(
                event_type="incident_status_changed",
                payload={"event": "STATUS_CHANGED", "incident": updated}
            )
        except Exception as ws_err:
            logger.warning(f"Could not broadcast Socket.IO status change: {ws_err}")

        return jsonify({
            "status": "success",
            "message": f"Incident #{incident_id} updated to {new_status}.",
            "data": updated
        }), 200

    except Exception as e:
        logger.error(f"Error updating status for incident #{incident_id}: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not update emergency incident status.",
            "status_code": 500
        }), 500
