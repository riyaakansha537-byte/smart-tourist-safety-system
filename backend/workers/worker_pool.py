# ============================================================
# Smart Tourist Safety and Emergency Response System
# OS Concept: Multithreading & Worker Pool (Phase 11)
# ============================================================

import queue
import threading
import time
from typing import Any, Dict, List, Optional
from backend.scheduler.priority_queue import EmergencyEvent, EmergencyPriorityQueue, scheduler
from backend.workers.gps_worker import GPSWorker
from backend.workers.sos_worker import SOSWorker
from backend.workers.geofence_worker import GeofenceWorker
from backend.utils.logger import logger

DEFAULT_WORKER_POOL_SIZE = 3

class WorkerPool:
    """
    Multithreaded Worker Pool managing background consumer threads.
    Continuously consumes events from the priority queue and dispatches
    them to specialized workers according to OS priority scheduling.
    """

    def __init__(
        self,
        pool_size: int = DEFAULT_WORKER_POOL_SIZE,
        priority_scheduler: Optional[EmergencyPriorityQueue] = None,
        resource_manager=None
    ):
        self.pool_size = max(1, pool_size)
        self.scheduler = priority_scheduler or scheduler
        self.resource_manager = resource_manager

        self._threads: List[threading.Thread] = []
        self._running = False
        self._lock = threading.Lock()

        # Telemetry metrics
        self._processed_counts: Dict[str, int] = {}
        self._worker_task_counts: Dict[str, int] = {}

    def start(self) -> None:
        """Starts worker threads in the pool."""
        with self._lock:
            if self._running:
                logger.warning("[WorkerPool] Worker pool is already running.")
                return

            self._running = True
            self._threads.clear()

            for i in range(1, self.pool_size + 1):
                name = f"EmergencyWorker-{i}"
                self._worker_task_counts[name] = 0
                thread = threading.Thread(
                    target=self._worker_loop,
                    name=name,
                    daemon=True
                )
                self._threads.append(thread)
                thread.start()

            logger.info(f"[WorkerPool] Started {self.pool_size} background worker threads.")

    def stop(self, timeout: float = 3.0) -> None:
        """Signals worker threads to terminate and waits for completion."""
        with self._lock:
            if not self._running:
                return
            self._running = False

        logger.info("[WorkerPool] Stopping worker pool...")
        for thread in self._threads:
            thread.join(timeout=timeout)
        self._threads.clear()
        logger.info("[WorkerPool] Worker pool stopped cleanly.")

    def is_running(self) -> bool:
        """Returns True if worker pool threads are active."""
        return self._running

    def _worker_loop(self) -> None:
        """Core loop executed by each worker thread."""
        worker_name = threading.current_thread().name
        logger.info(f"[{worker_name}] Worker thread started and listening for priority events...")

        while self._running:
            try:
                # Dequeue next highest-priority event (blocking with timeout so loop checks _running)
                event = self.scheduler.dequeue(block=True, timeout=0.5)
                self._process_event(worker_name, event)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"[{worker_name}] Unexpected error processing event: {e}")

        logger.info(f"[{worker_name}] Worker thread terminating.")

    def _process_event(self, worker_name: str, event: EmergencyEvent) -> Dict[str, Any]:
        """Routes event to specific worker handler based on event type."""
        result = None

        if event.event_type == "GPS_UPDATE":
            result = GPSWorker.process_event(event, scheduler_instance=self.scheduler)
        elif event.event_type == "DANGEROUS_ZONE":
            result = GeofenceWorker.process_event(event)
        elif event.event_type in ("CRITICAL_ACCIDENT", "SOS", "SAFETY_ALERT"):
            result = SOSWorker.process_event(event, resource_manager=self.resource_manager)
        else:
            result = SOSWorker.process_event(event, resource_manager=self.resource_manager)

        # Update telemetry
        with self._lock:
            self._worker_task_counts[worker_name] = self._worker_task_counts.get(worker_name, 0) + 1
            self._processed_counts[event.event_type] = self._processed_counts.get(event.event_type, 0) + 1

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Returns runtime execution statistics for thread pool monitoring."""
        with self._lock:
            active_threads = [t.name for t in self._threads if t.is_alive()]
            return {
                "running": self._running,
                "pool_size": self.pool_size,
                "active_threads_count": len(active_threads),
                "active_threads": active_threads,
                "tasks_by_worker": dict(self._worker_task_counts),
                "tasks_by_type": dict(self._processed_counts),
                "total_processed": sum(self._processed_counts.values()),
            }

# Global worker pool instance (pool_size=3)
worker_pool: WorkerPool = WorkerPool(pool_size=DEFAULT_WORKER_POOL_SIZE)
