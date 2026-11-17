# ============================================================
# Smart Tourist Safety and Emergency Response System
# Authority Dashboard API Routes (Phase 16)
# ============================================================

from flask import Blueprint, jsonify, request
from backend.db.repositories import (
    DashboardRepository,
    EmergencyRepository,
    LogRepository,
)
from backend.resource_manager import resource_manager
from backend.scheduler.priority_queue import scheduler
from backend.workers.worker_pool import worker_pool
from backend.utils.logger import logger

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/ping", methods=["GET"])
def ping_dashboard():
    """Diagnostic ping endpoint for Dashboard blueprint."""
    return jsonify({
        "module": "dashboard",
        "status": "active",
        "message": "Authority dashboard API blueprint operational"
    }), 200

@dashboard_bp.route("/summary", methods=["GET"])
def get_dashboard_summary():
    """
    Returns consolidated high-level overview metrics:
      - Database counts (tourists, active incidents, available resources/teams)
      - OS Scheduler status (queue length)
      - OS Banker's Algorithm status (deadlock-free safe state)
      - OS Multithreading status (active worker threads)
    """
    try:
        counts = DashboardRepository.get_summary_counts()
        banker_state = resource_manager.banker.get_state()
        scheduler_stats = scheduler.get_stats()
        worker_stats = worker_pool.get_stats()

        summary_payload = {
            "status": "success",
            "metrics": {
                **counts,
                "scheduler_queue_size": scheduler_stats["current_size"],
                "is_safe_state": banker_state["is_safe"],
                "active_worker_threads": worker_stats["active_threads_count"],
            },
            "banker_safe_sequence": banker_state["safe_sequence"],
        }
        return jsonify(summary_payload), 200
    except Exception as e:
        logger.error(f"Error compiling dashboard summary: {e}")
        return jsonify({
            "error": "Internal Error",
            "message": "Could not compile dashboard summary.",
            "status_code": 500
        }), 500

@dashboard_bp.route("/active-emergencies", methods=["GET"])
def get_active_emergencies():
    """Returns currently unresolved emergency incidents ordered by Priority (1=Accident first)."""
    limit = request.args.get("limit", default=50, type=int)
    offset = request.args.get("offset", default=0, type=int)

    try:
        # Fetch non-resolved incidents
        all_incidents = EmergencyRepository.get_incidents(limit=limit, offset=offset)
        active = [inc for inc in all_incidents if inc["status"] not in ("RESOLVED", "FAILED")]
        return jsonify({
            "status": "success",
            "count": len(active),
            "data": active
        }), 200
    except Exception as e:
        logger.error(f"Error fetching active emergencies: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve active emergencies.",
            "status_code": 500
        }), 500

@dashboard_bp.route("/logs", methods=["GET"])
def get_dashboard_logs():
    """Returns recent immutable audit logs from emergency_logs."""
    limit = request.args.get("limit", default=50, type=int)
    offset = request.args.get("offset", default=0, type=int)
    limit = max(1, min(limit, 200))
    offset = max(0, offset)

    try:
        logs = LogRepository.get_recent_logs(limit=limit, offset=offset)
        return jsonify({
            "status": "success",
            "count": len(logs),
            "limit": limit,
            "offset": offset,
            "data": logs
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {e}")
        return jsonify({
            "error": "Database Error",
            "message": "Could not retrieve audit logs.",
            "status_code": 500
        }), 500

@dashboard_bp.route("/banker-state", methods=["GET"])
def get_banker_state():
    """
    Returns full mathematical data structures of the Banker's Algorithm
    for real-time dashboard inspection and viva demonstration.
    """
    try:
        state = resource_manager.banker.get_state()
        sync_metrics = resource_manager.sync.get_sync_metrics()
        return jsonify({
            "status": "success",
            "banker_matrices": state,
            "synchronization": sync_metrics
        }), 200
    except Exception as e:
        logger.error(f"Error fetching Banker's state: {e}")
        return jsonify({
            "error": "Internal Error",
            "message": "Could not retrieve Banker's algorithm state.",
            "status_code": 500
        }), 500

@dashboard_bp.route("/scheduler", methods=["GET"])
def get_scheduler_status():
    """Returns PriorityQueue metrics and snapshot of pending events."""
    try:
        stats = scheduler.get_stats()
        queued_events = [ev.to_dict() for ev in scheduler.get_all_events()]
        return jsonify({
            "status": "success",
            "stats": stats,
            "queued_events": queued_events
        }), 200
    except Exception as e:
        logger.error(f"Error fetching scheduler status: {e}")
        return jsonify({
            "error": "Internal Error",
            "message": "Could not retrieve scheduler status.",
            "status_code": 500
        }), 500

@dashboard_bp.route("/worker-stats", methods=["GET"])
def get_worker_stats():
    """Returns multithreaded worker pool metrics."""
    try:
        stats = worker_pool.get_stats()
        return jsonify({
            "status": "success",
            "worker_pool": stats
        }), 200
    except Exception as e:
        logger.error(f"Error fetching worker pool stats: {e}")
        return jsonify({
            "error": "Internal Error",
            "message": "Could not retrieve worker statistics.",
            "status_code": 500
        }), 500
