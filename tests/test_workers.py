# ============================================================
# Smart Tourist Safety and Emergency Response System
# Tests: OS Multithreading & Worker Pool (Phase 11)
# ============================================================

import time
from unittest.mock import MagicMock, patch
import pytest
from backend.scheduler.priority_queue import (
    EmergencyEvent,
    EmergencyPriorityQueue,
    PRIORITY_CRITICAL_ACCIDENT,
    PRIORITY_SOS,
    PRIORITY_DANGEROUS_ZONE,
    PRIORITY_GPS_UPDATE,
)
from backend.workers.gps_worker import GPSWorker
from backend.workers.sos_worker import SOSWorker
from backend.workers.geofence_worker import GeofenceWorker
from backend.workers.notification_worker import NotificationWorker
from backend.workers.worker_pool import WorkerPool

class TestIndividualWorkers:
    """Tests unit logic of specialized event workers."""

    def test_gps_worker_normal_update(self):
        event = EmergencyEvent(
            priority=PRIORITY_GPS_UPDATE,
            tourist_id=1,
            event_type="GPS_UPDATE",
            latitude=15.55,
            longitude=73.75,
            payload={"zone": None},
        )
        res = GPSWorker.process_event(event)
        assert res["status"] == "processed"
        assert res["geofence_breach"] is False
        assert res["escalated_event_id"] is None

    def test_gps_worker_dangerous_zone_escalation(self):
        pq = EmergencyPriorityQueue()
        event = EmergencyEvent(
            priority=PRIORITY_GPS_UPDATE,
            tourist_id=2,
            event_type="GPS_UPDATE",
            latitude=15.4925,
            longitude=73.7735,
            payload={
                "zone": {
                    "zone_name": "Aguada Sea Cliff",
                    "zone_type": "DANGEROUS",
                    "risk_level": "HIGH",
                }
            },
        )
        res = GPSWorker.process_event(event, scheduler_instance=pq)
        assert res["status"] == "processed"
        assert res["geofence_breach"] is True
        assert res["escalated_event_id"] is not None

        # Verify escalated event was enqueued with Priority 3
        assert pq.size() == 1
        escalated = pq.dequeue()
        assert escalated.priority == PRIORITY_DANGEROUS_ZONE
        assert escalated.event_type == "DANGEROUS_ZONE"
        assert escalated.tourist_id == 2

    @patch("backend.workers.geofence_worker.EmergencyRepository.update_incident_status")
    @patch("backend.workers.notification_worker.broadcast_emergency_update")
    def test_geofence_worker_processes_breach(self, mock_broadcast, mock_update):
        mock_update.return_value = {"incident_id": 50, "status": "PROCESSING"}
        event = EmergencyEvent(
            priority=PRIORITY_DANGEROUS_ZONE,
            incident_id=50,
            tourist_id=3,
            event_type="DANGEROUS_ZONE",
            latitude=15.0872,
            longitude=74.2081,
            payload={"zone": {"zone_name": "Netravali Forest", "risk_level": "HIGH"}},
        )
        res = GeofenceWorker.process_event(event)
        assert res["status"] == "processed"
        assert res["incident_id"] == 50
        mock_update.assert_called_once()
        mock_broadcast.assert_called_once()

    @patch("backend.workers.sos_worker.EmergencyRepository.update_incident_status")
    @patch("backend.workers.notification_worker.broadcast_emergency_update")
    def test_sos_worker_critical_accident(self, mock_broadcast, mock_update):
        mock_update.return_value = {"incident_id": 10, "status": "PROCESSING"}
        mock_res_mgr = MagicMock()
        mock_res_mgr.request_allocation.return_value = {"allocated": True, "ambulance_id": 1}

        event = EmergencyEvent(
            priority=PRIORITY_CRITICAL_ACCIDENT,
            incident_id=10,
            tourist_id=5,
            event_type="CRITICAL_ACCIDENT",
            latitude=15.55,
            longitude=73.75,
        )
        res = SOSWorker.process_event(event, resource_manager=mock_res_mgr)
        assert res["status"] == "processed"
        assert res["allocation"]["allocated"] is True
        mock_update.assert_called_once()
        mock_res_mgr.request_allocation.assert_called_once()
        mock_broadcast.assert_called_once()

    @patch("backend.workers.notification_worker.broadcast_emergency_update")
    def test_notification_worker_dispatch(self, mock_broadcast):
        res = NotificationWorker.dispatch(
            event_type="test_alert",
            message="Test message",
            payload={"id": 123},
        )
        assert res["delivered"] is True
        assert res["event_type"] == "test_alert"
        mock_broadcast.assert_called_once()

class TestWorkerPoolConcurrency:
    """Tests multithreaded worker pool lifecycle and task consumption."""

    def test_worker_pool_start_and_stop(self):
        pq = EmergencyPriorityQueue()
        pool = WorkerPool(pool_size=3, priority_scheduler=pq)

        assert not pool.is_running()
        pool.start()
        assert pool.is_running()

        stats = pool.get_stats()
        assert stats["running"] is True
        assert stats["pool_size"] == 3
        assert stats["active_threads_count"] == 3
        assert len(stats["active_threads"]) == 3

        pool.stop(timeout=1.0)
        assert not pool.is_running()

    def test_worker_pool_processes_queued_events(self):
        pq = EmergencyPriorityQueue()
        pool = WorkerPool(pool_size=3, priority_scheduler=pq)

        # Enqueue mixed priority events
        pq.enqueue(EmergencyEvent(priority=PRIORITY_GPS_UPDATE, event_type="GPS_UPDATE"))
        pq.enqueue(EmergencyEvent(priority=PRIORITY_SOS, event_type="SOS"))
        pq.enqueue(EmergencyEvent(priority=PRIORITY_CRITICAL_ACCIDENT, event_type="CRITICAL_ACCIDENT"))
        pq.enqueue(EmergencyEvent(priority=PRIORITY_DANGEROUS_ZONE, event_type="DANGEROUS_ZONE"))

        assert pq.size() == 4

        pool.start()

        # Wait briefly for workers to consume all 4 tasks
        start_time = time.time()
        while pq.size() > 0 and (time.time() - start_time) < 3.0:
            time.sleep(0.05)

        pool.stop(timeout=1.0)

        assert pq.size() == 0
        stats = pool.get_stats()
        assert stats["total_processed"] == 4
        assert stats["tasks_by_type"].get("CRITICAL_ACCIDENT") == 1
        assert stats["tasks_by_type"].get("SOS") == 1
        assert stats["tasks_by_type"].get("DANGEROUS_ZONE") == 1
        assert stats["tasks_by_type"].get("GPS_UPDATE") == 1
