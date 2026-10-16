# ============================================================
# Smart Tourist Safety and Emergency Response System
# OS Concept: Priority Scheduling (Phase 10)
# ============================================================

import queue
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.utils.logger import logger

_sequence_lock = threading.Lock()
_sequence_value = 0


def _next_sequence() -> int:
    """Provide a deterministic FIFO tie-breaker when timestamps are equal."""
    global _sequence_value
    with _sequence_lock:
        _sequence_value += 1
        return _sequence_value

# Priority mapping (1=Highest urgency, 5=Lowest urgency)
PRIORITY_CRITICAL_ACCIDENT = 1
PRIORITY_SOS = 2
PRIORITY_DANGEROUS_ZONE = 3
PRIORITY_SAFETY_ALERT = 4
PRIORITY_GPS_UPDATE = 5

EVENT_TYPE_PRIORITIES = {
    "CRITICAL_ACCIDENT": PRIORITY_CRITICAL_ACCIDENT,
    "SOS": PRIORITY_SOS,
    "DANGEROUS_ZONE": PRIORITY_DANGEROUS_ZONE,
    "SAFETY_ALERT": PRIORITY_SAFETY_ALERT,
    "GPS_UPDATE": PRIORITY_GPS_UPDATE,
}

@dataclass(order=True)
class EmergencyEvent:
    """
    Encapsulates a schedulable emergency or telemetry event.
    Implements total ordering for OS Priority Scheduling:
      1. Primary key: priority (ascending integer, 1 is highest priority)
      2. Secondary key (tie-breaker): timestamp (FIFO ordering for identical priorities)
    """
    priority: int
    timestamp: float = field(default_factory=time.time)
    sequence: int = field(default_factory=_next_sequence)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8], compare=False)
    incident_id: Optional[int] = field(default=None, compare=False)
    tourist_id: int = field(default=0, compare=False)
    event_type: str = field(default="SAFETY_ALERT", compare=False)
    latitude: float = field(default=0.0, compare=False)
    longitude: float = field(default=0.0, compare=False)
    payload: Dict[str, Any] = field(default_factory=dict, compare=False)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        compare=False
    )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes event to dictionary representation."""
        return {
            "event_id": self.event_id,
            "incident_id": self.incident_id,
            "tourist_id": self.tourist_id,
            "event_type": self.event_type,
            "priority": self.priority,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "created_at": self.created_at,
        }

class EmergencyPriorityQueue:
    """
    Thread-safe Priority Queue implementing Operating Systems Priority Scheduling.
    Wraps Python's queue.PriorityQueue with inspection, snapshot, and telemetry features.
    """

    def __init__(self, maxsize: int = 0):
        self._queue: queue.PriorityQueue = queue.PriorityQueue(maxsize=maxsize)
        self._lock: threading.Lock = threading.Lock()
        self._enqueued_count: int = 0
        self._dequeued_count: int = 0

    def enqueue(self, event: EmergencyEvent) -> None:
        """
        Enqueues an event into the priority queue according to its priority level.
        Thread-safe operation.
        """
        with self._lock:
            self._enqueued_count += 1
        self._queue.put(event)
        logger.info(
            f"[PriorityQueue] Enqueued Event #{event.event_id} "
            f"[{event.event_type}] Priority={event.priority} (Queue Size={self.size()})"
        )

    def dequeue(self, block: bool = True, timeout: Optional[float] = None) -> EmergencyEvent:
        """
        Dequeues the highest-priority event currently waiting in the queue.
        Blocks until an item is available if block is True.
        Raises queue.Empty if non-blocking or timeout expires.
        """
        event = self._queue.get(block=block, timeout=timeout)
        with self._lock:
            self._dequeued_count += 1
        self._queue.task_done()
        logger.info(
            f"[PriorityQueue] Dequeued Event #{event.event_id} "
            f"[{event.event_type}] Priority={event.priority} (Remaining={self.size()})"
        )
        return event

    def peek(self) -> Optional[EmergencyEvent]:
        """
        Inspects the highest-priority item in the queue without removing it.
        Thread-safe non-destructive inspection.
        """
        with self._queue.mutex:
            if not self._queue.queue:
                return None
            return self._queue.queue[0]

    def size(self) -> int:
        """Returns current number of items waiting in the priority queue."""
        return self._queue.qsize()

    def is_empty(self) -> bool:
        """Returns True if priority queue contains no items."""
        return self._queue.empty()

    def get_all_events(self) -> List[EmergencyEvent]:
        """
        Returns a sorted snapshot of all pending events currently in the queue
        without modifying or dequeuing them.
        """
        with self._queue.mutex:
            # Copy and sort by priority order
            events = sorted(list(self._queue.queue))
            return events

    def get_stats(self) -> Dict[str, Any]:
        """Returns runtime scheduler metrics."""
        with self._lock:
            return {
                "current_size": self.size(),
                "total_enqueued": self._enqueued_count,
                "total_dequeued": self._dequeued_count,
                "is_empty": self.is_empty(),
            }

    def clear(self) -> None:
        """Removes all events currently waiting in the queue."""
        with self._queue.mutex:
            self._queue.queue.clear()
            logger.info("[PriorityQueue] Cleared all pending events.")

    def enqueue_from_incident(self, incident: Dict[str, Any]) -> EmergencyEvent:
        """Factory helper: converts a database incident dictionary to an EmergencyEvent."""
        event_type = incident.get("incident_type", "SAFETY_ALERT")
        priority = incident.get("priority", EVENT_TYPE_PRIORITIES.get(event_type, PRIORITY_SAFETY_ALERT))
        created_at = incident.get("created_at")
        if hasattr(created_at, "timestamp"):
            timestamp = created_at.timestamp()
        elif isinstance(created_at, str):
            try:
                timestamp = datetime.fromisoformat(created_at.replace("Z", "+00:00")).timestamp()
            except ValueError:
                timestamp = time.time()
        else:
            timestamp = time.time()
        event = EmergencyEvent(
            priority=priority,
            timestamp=timestamp,
            incident_id=incident.get("incident_id"),
            tourist_id=incident.get("tourist_id", 0),
            event_type=event_type,
            latitude=float(incident.get("latitude", 0.0)),
            longitude=float(incident.get("longitude", 0.0)),
            payload={"description": incident.get("description", "")},
        )
        self.enqueue(event)
        return event

    def enqueue_from_location(self, location: Dict[str, Any]) -> EmergencyEvent:
        """Factory helper: converts a GPS telemetry dictionary to a low-priority EmergencyEvent."""
        zone = location.get("zone")
        if zone and zone.get("zone_type") == "DANGEROUS":
            event_type = "DANGEROUS_ZONE"
            priority = PRIORITY_DANGEROUS_ZONE
        else:
            event_type = "GPS_UPDATE"
            priority = PRIORITY_GPS_UPDATE

        event = EmergencyEvent(
            priority=priority,
            tourist_id=location.get("tourist_id", 0),
            event_type=event_type,
            latitude=float(location.get("latitude", 0.0)),
            longitude=float(location.get("longitude", 0.0)),
            payload={"zone": zone, "location_id": location.get("location_id")},
        )
        self.enqueue(event)
        return event

# Global shared instance of the emergency priority scheduler
scheduler: EmergencyPriorityQueue = EmergencyPriorityQueue()
