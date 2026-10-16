# ============================================================
# Smart Tourist Safety and Emergency Response System
# Scheduler Package (OS Priority Scheduling)
# ============================================================

from backend.scheduler.priority_queue import (
    EmergencyEvent,
    EmergencyPriorityQueue,
    scheduler,
    PRIORITY_CRITICAL_ACCIDENT,
    PRIORITY_SOS,
    PRIORITY_DANGEROUS_ZONE,
    PRIORITY_SAFETY_ALERT,
    PRIORITY_GPS_UPDATE,
)

__all__ = [
    "EmergencyEvent",
    "EmergencyPriorityQueue",
    "scheduler",
    "PRIORITY_CRITICAL_ACCIDENT",
    "PRIORITY_SOS",
    "PRIORITY_DANGEROUS_ZONE",
    "PRIORITY_SAFETY_ALERT",
    "PRIORITY_GPS_UPDATE",
]
