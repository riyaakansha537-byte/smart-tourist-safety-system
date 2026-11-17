# ============================================================
# Smart Tourist Safety and Emergency Response System
# Tests: Synchronization & Banker's Algorithm (Phases 12, 13, 14)
# ============================================================

import threading
import time
from unittest.mock import MagicMock, patch
import pytest
from backend.resource_manager.synchronization import SynchronizationManager
from backend.resource_manager.bankers_algorithm import BankersAlgorithm
from backend.resource_manager.resource_manager import ResourceManager

class TestSynchronizationManager:
    """Tests Mutex Locks and Counting Semaphores (OS Phase 12)."""

    def test_mutex_mutual_exclusion(self):
        sync = SynchronizationManager()
        counter = 0
        num_threads = 10
        increments_per_thread = 50

        def increment_worker():
            nonlocal counter
            for _ in range(increments_per_thread):
                with sync.critical_section():
                    current = counter
                    time.sleep(0.0001)  # introduce tiny delay to test race conditions
                    counter = current + 1

        threads = [threading.Thread(target=increment_worker) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert counter == num_threads * increments_per_thread
        metrics = sync.get_sync_metrics()
        assert metrics["total_locks_acquired"] == num_threads * increments_per_thread

    def test_semaphore_throttles_concurrency(self):
        # Allow max 2 concurrent dispatches
        sync = SynchronizationManager(max_concurrent_allocations=2)
        active_concurrent = 0
        max_seen = 0
        lock = threading.Lock()

        def dispatch_worker():
            nonlocal active_concurrent, max_seen
            with sync.acquire_dispatch_permit(timeout=2.0) as permit:
                assert permit is True
                with lock:
                    active_concurrent += 1
                    if active_concurrent > max_seen:
                        max_seen = active_concurrent
                time.sleep(0.05)
                with lock:
                    active_concurrent -= 1

        threads = [threading.Thread(target=dispatch_worker) for _ in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert max_seen <= 2

class TestBankersAlgorithm:
    """Tests Deadlock Avoidance Safety Algorithm (OS Phase 14)."""

    def test_initial_state_safe(self):
        banker = BankersAlgorithm(initial_available={"AMBULANCE": 3, "RESCUE_TEAM": 3, "HELICOPTER": 2})
        is_safe, seq = banker.is_safe_state()
        assert is_safe is True
        assert seq == []

    def test_safe_request_granted(self):
        # 3 Ambulances, 3 Rescue Teams, 2 Helicopters
        banker = BankersAlgorithm(initial_available={"AMBULANCE": 3, "RESCUE_TEAM": 3, "HELICOPTER": 2})
        banker.register_process(process_id=1, max_demand={"AMBULANCE": 2, "RESCUE_TEAM": 1, "HELICOPTER": 0})

        # Request 1 Ambulance
        granted, msg, seq = banker.request_resources(process_id=1, request_vector={"AMBULANCE": 1, "RESCUE_TEAM": 0, "HELICOPTER": 0})
        assert granted is True
        assert seq == [1]
        assert banker.available["AMBULANCE"] == 2
        assert banker.allocation[1]["AMBULANCE"] == 1
        assert banker.need[1]["AMBULANCE"] == 1

    def test_request_exceeds_need_rejected(self):
        banker = BankersAlgorithm(initial_available={"AMBULANCE": 2, "RESCUE_TEAM": 2, "HELICOPTER": 1})
        banker.register_process(process_id=1, max_demand={"AMBULANCE": 1, "RESCUE_TEAM": 0, "HELICOPTER": 0})

        # Request 2 Ambulances when Max Claim is only 1
        granted, msg, seq = banker.request_resources(process_id=1, request_vector={"AMBULANCE": 2, "RESCUE_TEAM": 0, "HELICOPTER": 0})
        assert granted is False
        assert "exceeded its maximum claim" in msg

    def test_request_exceeds_available_rejected(self):
        banker = BankersAlgorithm(initial_available={"AMBULANCE": 1, "RESCUE_TEAM": 1, "HELICOPTER": 0})
        banker.register_process(process_id=1, max_demand={"AMBULANCE": 2, "RESCUE_TEAM": 1, "HELICOPTER": 0})

        # Request 2 Ambulances when only 1 is available
        granted, msg, seq = banker.request_resources(process_id=1, request_vector={"AMBULANCE": 2, "RESCUE_TEAM": 0, "HELICOPTER": 0})
        assert granted is False
        assert "Resources unavailable" in msg

    def test_unsafe_state_deadlock_avoidance_rollback(self):
        # Create classical deadlock avoidance scenario:
        # Available: [1, 0, 0]
        # P1 needs [2, 0, 0], Allocated [1, 0, 0] -> Need [1, 0, 0]
        # P2 needs [2, 0, 0], Allocated [0, 0, 0] -> Need [2, 0, 0]
        banker = BankersAlgorithm(initial_available={"AMBULANCE": 1, "RESCUE_TEAM": 0, "HELICOPTER": 0})
        banker.register_process(process_id=1, max_demand={"AMBULANCE": 2, "RESCUE_TEAM": 0, "HELICOPTER": 0})
        banker.register_process(process_id=2, max_demand={"AMBULANCE": 2, "RESCUE_TEAM": 0, "HELICOPTER": 0})

        # If P2 requests the last 1 ambulance, Available becomes 0.
        # Neither P1 (needs 1) nor P2 (needs 1) can finish! Deadlock would occur.
        granted, msg, seq = banker.request_resources(process_id=2, request_vector={"AMBULANCE": 1, "RESCUE_TEAM": 0, "HELICOPTER": 0})

        # Must be rejected by Banker's algorithm!
        assert granted is False
        assert "Deadlock Avoidance" in msg
        # Verify rollback: Available ambulance restored to 1, P2 allocation remains 0
        assert banker.available["AMBULANCE"] == 1
        assert banker.allocation[2]["AMBULANCE"] == 0

    def test_release_and_unregistration(self):
        banker = BankersAlgorithm(initial_available={"AMBULANCE": 2, "RESCUE_TEAM": 2, "HELICOPTER": 1})
        banker.register_process(process_id=1, max_demand={"AMBULANCE": 1, "RESCUE_TEAM": 1, "HELICOPTER": 0})
        banker.request_resources(process_id=1, request_vector={"AMBULANCE": 1, "RESCUE_TEAM": 1, "HELICOPTER": 0})
        assert banker.available["AMBULANCE"] == 1

        reclaimed = banker.unregister_process(process_id=1)
        assert reclaimed["AMBULANCE"] == 1
        assert banker.available["AMBULANCE"] == 2
        assert 1 not in banker.max_claim

class TestResourceManager:
    """Tests integrated Resource Manager orchestration (OS Phase 13)."""

    @patch("backend.resource_manager.resource_manager.EmergencyRepository.update_incident_status")
    @patch("backend.resource_manager.resource_manager.ResourceRepository.create_assignment")
    @patch("backend.resource_manager.resource_manager.ResourceRepository.update_resource_status")
    @patch("backend.resource_manager.resource_manager.ResourceRepository.get_available_resources")
    def test_request_allocation_safe_success(
        self,
        mock_get_ambs,
        mock_update_res,
        mock_create_asgn,
        mock_update_inc
    ):
        mock_get_ambs.return_value = [{"resource_id": 1, "resource_name": "Ambulance-Alpha"}]
        mock_create_asgn.return_value = {"assignment_id": 100}

        banker = BankersAlgorithm(initial_available={"AMBULANCE": 3, "RESCUE_TEAM": 3, "HELICOPTER": 1})
        rm = ResourceManager(banker=banker)

        res = rm.request_allocation(
            incident_id=10,
            demands={"AMBULANCE": 1, "RESCUE_TEAM": 0, "HELICOPTER": 0},
            incident_type="SOS"
        )

        assert res["allocated"] is True
        assert res["incident_id"] == 10
        assert len(res["resources_assigned"]) == 1
        mock_update_inc.assert_called_once()

    @patch("backend.resource_manager.resource_manager.EmergencyRepository.update_incident_status")
    @patch("backend.resource_manager.resource_manager.ResourceRepository.release_incident_assignments")
    def test_release_allocation_success(self, mock_release_db, mock_update_inc):
        mock_release_db.return_value = 2
        banker = BankersAlgorithm(initial_available={"AMBULANCE": 2, "RESCUE_TEAM": 2, "HELICOPTER": 1})
        banker.register_process(process_id=20, max_demand={"AMBULANCE": 1, "RESCUE_TEAM": 0, "HELICOPTER": 0})
        banker.request_resources(process_id=20, request_vector={"AMBULANCE": 1, "RESCUE_TEAM": 0, "HELICOPTER": 0})

        rm = ResourceManager(banker=banker)
        res = rm.release_allocation(incident_id=20)

        assert res["status"] == "success"
        assert res["released_assignments"] == 2
        assert res["reclaimed_vector"]["AMBULANCE"] == 1
        assert banker.available["AMBULANCE"] == 2
