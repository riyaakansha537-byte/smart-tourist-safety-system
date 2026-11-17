# ============================================================
# Smart Tourist Safety and Emergency Response System
# Resource & Rescue Team Management API Routes (Phase 15)
# ============================================================

from flask import Blueprint, jsonify, request
from backend.db.repositories import (
    ResourceRepository,
    RescueTeamRepository,
    RecordNotFoundError,
)
from backend.resource_manager import resource_manager
from backend.utils.logger import logger

resource_bp = Blueprint("resources", __name__)

@resource_bp.route("/ping", methods=["GET"])
def ping_resources():
    """Diagnostic ping endpoint for Resource blueprint."""
    return jsonify({
        "module": "resources",
        "status": "active",
        "message": "Resource management API blueprint operational"
    }), 200

@resource_bp.route("", methods=["GET"])
def list_resources():
    """Returns list of emergency response apparatus (ambulances, helicopters, boats)."""
    res_type = request.args.get("type")
    status = request.args.get("status")

    try:
        resources = ResourceRepository.get_all_resources(
            resource_type=res_type,
            status=status
        )
        return jsonify({
            "status": "success",
            "count": len(resources),
            "data": resources
        }), 200
    except Exception as e:
        logger.error(f"Error listing resources: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve resources.",
            "status_code": 500
        }), 500

@resource_bp.route("/available", methods=["GET"])
def list_available_resources():
    """Returns list of apparatus currently AVAILABLE for dispatch."""
    res_type = request.args.get("type")
    try:
        resources = ResourceRepository.get_available_resources(resource_type=res_type)
        return jsonify({
            "status": "success",
            "count": len(resources),
            "data": resources
        }), 200
    except Exception as e:
        logger.error(f"Error listing available resources: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve available resources.",
            "status_code": 500
        }), 500

@resource_bp.route("/<int:resource_id>", methods=["GET"])
def get_resource(resource_id: int):
    """Retrieves single resource profile by ID."""
    try:
        resource = ResourceRepository.get_resource_by_id(resource_id)
        if not resource:
            return jsonify({
                "error": "Not Found",
                "message": f"Resource #{resource_id} not found.",
                "status_code": 404
            }), 404
        return jsonify({
            "status": "success",
            "data": resource
        }), 200
    except Exception as e:
        logger.error(f"Error fetching resource #{resource_id}: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve resource.",
            "status_code": 500
        }), 500

@resource_bp.route("/teams", methods=["GET"])
def list_teams():
    """Returns list of specialized emergency response teams."""
    status = request.args.get("status")
    try:
        teams = RescueTeamRepository.get_all_teams(status=status)
        return jsonify({
            "status": "success",
            "count": len(teams),
            "data": teams
        }), 200
    except Exception as e:
        logger.error(f"Error listing teams: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve rescue teams.",
            "status_code": 500
        }), 500

@resource_bp.route("/teams/available", methods=["GET"])
def list_available_teams():
    """Returns list of rescue teams with open capacity."""
    try:
        teams = RescueTeamRepository.get_available_teams()
        return jsonify({
            "status": "success",
            "count": len(teams),
            "data": teams
        }), 200
    except Exception as e:
        logger.error(f"Error listing available teams: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve available rescue teams.",
            "status_code": 500
        }), 500

@resource_bp.route("/allocate", methods=["POST"])
def allocate_resources():
    """
    Submits a resource allocation request evaluated by the Banker's Algorithm.
    Prevents deadlock by denying requests that would lead to unsafe states.
    Payload: {"incident_id": 1, "demands": {"AMBULANCE": 1, "RESCUE_TEAM": 1}}
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "incident_id" not in data:
        return jsonify({
            "error": "Validation Error",
            "message": "Field 'incident_id' is required.",
            "status_code": 400
        }), 400

    incident_id = data["incident_id"]
    demands = data.get("demands", {"AMBULANCE": 1})
    incident_type = data.get("incident_type")

    result = resource_manager.request_allocation(
        incident_id=incident_id,
        demands=demands,
        incident_type=incident_type
    )

    if not result.get("allocated"):
        status_code = result.get("status_code", 409)
        return jsonify(result), status_code

    return jsonify(result), 200

@resource_bp.route("/release", methods=["POST"])
def release_resources():
    """
    Releases all allocated resources for an incident back to the pool.
    Payload: {"incident_id": 1}
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "incident_id" not in data:
        return jsonify({
            "error": "Validation Error",
            "message": "Field 'incident_id' is required.",
            "status_code": 400
        }), 400

    incident_id = data["incident_id"]
    result = resource_manager.release_allocation(incident_id=incident_id)
    return jsonify(result), 200

@resource_bp.route("/assignments/<int:incident_id>", methods=["GET"])
def get_assignments(incident_id: int):
    """Retrieves all vehicle and personnel assignments for an incident."""
    try:
        assignments = ResourceRepository.get_incident_assignments(incident_id)
        return jsonify({
            "status": "success",
            "incident_id": incident_id,
            "count": len(assignments),
            "data": assignments
        }), 200
    except Exception as e:
        logger.error(f"Error fetching assignments for incident #{incident_id}: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve assignments.",
            "status_code": 500
        }), 500
