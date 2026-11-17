# ============================================================
# Smart Tourist Safety and Emergency Response System
# Tests: OS Priority Queue & Event Scheduling (Phase 10)
# ============================================================

import queue
import threading
import time
import pytest
from backend.scheduler.priority_queue import (
    EmergencyEvent,
    EmergencyPriorityQueue,
    PRIORITY_CRITICAL_ACCIDENT,
    PRIORITY_SOS,
    PRIORITY_DANGEROUS_ZONE,
    PRIORITY_SAFETY_ALERT,
    PRIORITY_GPS_UPDATE,
)

class TestEmergencyEventOrdering:
    """Tests priority-based comparison and tie-breaking logic."""

    def test_higher_priority_dequeued_first(self):
        e1 = EmergencyEvent(priority=PRIORITY_CRITICAL_ACCIDENT, event_type="CRITICAL_ACCIDENT")
        e2 = EmergencyEvent(priority=PRIORITY_SOS, event_type="SOS")
        e3 = EmergencyEvent(priority=PRIORITY_GPS_UPDATE, event_type="GPS_UPDATE")

        assert e1 < e2
        assert e2 < e3
        assert e1 < e3

    def test_same_priority_fifo_ordering(self):
        # Two events with same priority (e.g. SOS) created with slight time delay
        t0 = time.time()
        e_first = EmergencyEvent(priority=PRIORITY_SOS, timestamp=t0, event_type="SOS")
        e_second = EmergencyEvent(priority=PRIORITY_SOS, timestamp=t0 + 0.05, event_type="SOS")

        assert e_first < e_second

class TestPriorityQueueOperations:
    """Tests enqueue, dequeue, peek, and stats operations on EmergencyPriorityQueue."""

    def test_priority_scheduling_order(self):
        pq = EmergencyPriorityQueue()

        # Insert in arbitrary reverse order: GPS (5), Alert (4), Zone (3), SOS (2), Accident (1)
        pq.enqueue(EmergencyEvent(priority=5, event_type="GPS_UPDATE"))
        pq.enqueue(EmergencyEvent(priority=4, event_type="SAFETY_ALERT"))
        pq.enqueue(EmergencyEvent(priority=2, event_type="SOS"))
        pq.enqueue(EmergencyEvent(priority=1, event_type="CRITICAL_ACCIDENT"))
        pq.enqueue(EmergencyEvent(priority=3, event_type="DANGEROUS_ZONE"))

        assert pq.size() == 5
        assert not pq.is_empty()

        # Verify dequeue order strictly follows priority (1, 2, 3, 4, 5)
        d1 = pq.dequeue(block=False)
        assert d1.priority == 1
        assert d1.event_type == "CRITICAL_ACCIDENT"

        d2 = pq.dequeue(block=False)
        assert d2.priority == 2
        assert d2.event_type == "SOS"

        d3 = pq.dequeue(block=False)
        assert d3.priority == 3
        assert d3.event_type == "DANGEROUS_ZONE"

        d4 = pq.dequeue(block=False)
        assert d4.priority == 4
        assert d4.event_type == "SAFETY_ALERT"

        d5 = pq.dequeue(block=False)
        assert d5.priority == 5
        assert d5.event_type == "GPS_UPDATE"

        assert pq.is_empty()

    def test_peek_does_not_remove_item(self):
        pq = EmergencyPriorityQueue()
        pq.enqueue(EmergencyEvent(priority=2, event_type="SOS"))
        pq.enqueue(EmergencyEvent(priority=1, event_type="CRITICAL_ACCIDENT"))

        top = pq.peek()
        assert top is not None
        assert top.priority == 1
        assert pq.size() == 2  # item not consumed

        # Dequeue consumes the item
        consumed = pq.dequeue()
        assert consumed.priority == 1
        assert pq.size() == 1

    def test_peek_empty_queue(self):
        pq = EmergencyPriorityQueue()
        assert pq.peek() is None

    def test_get_all_events_snapshot(self):
        pq = EmergencyPriorityQueue()
        pq.enqueue(EmergencyEvent(priority=4, event_type="SAFETY_ALERT"))
        pq.enqueue(EmergencyEvent(priority=1, event_type="CRITICAL_ACCIDENT"))

        snapshot = pq.get_all_events()
        assert len(snapshot) == 2
        assert snapshot[0].priority == 1
        assert snapshot[1].priority == 4
        assert pq.size() == 2  # queue unaffected

    def test_clear_queue(self):
        pq = EmergencyPriorityQueue()
        pq.enqueue(EmergencyEvent(priority=1))
        pq.enqueue(EmergencyEvent(priority=2))
        pq.clear()
        assert pq.is_empty()
        assert pq.size() == 0

    def test_dequeue_empty_raises(self):
        pq = EmergencyPriorityQueue()
        with pytest.raises(queue.Empty):
            pq.dequeue(block=False)

    def test_enqueue_from_incident(self):
        pq = EmergencyPriorityQueue()
        incident = {
            "incident_id": 99,
            "tourist_id": 1,
            "incident_type": "CRITICAL_ACCIDENT",
            "priority": 1,
            "latitude": 15.55,
            "longitude": 73.75,
            "description": "Road accident",
        }
        event = pq.enqueue_from_incident(incident)
        assert event.priority == 1
        assert event.incident_id == 99
        assert pq.size() == 1

    def test_enqueue_from_location(self):
        pq = EmergencyPriorityQueue()
        loc = {
            "location_id": 44,
            "tourist_id": 2,
            "latitude": 15.49,
            "longitude": 73.77,
            "zone": {"zone_type": "DANGEROUS", "zone_name": "Aguada"},
        }
        event = pq.enqueue_from_location(loc)
        assert event.priority == PRIORITY_DANGEROUS_ZONE
        assert event.event_type == "DANGEROUS_ZONE"

class TestMultiThreadedPriorityQueue:
    """Tests thread safety under high concurrency with multiple producer threads."""

    def test_concurrent_producers(self):
        pq = EmergencyPriorityQueue()
        num_producers = 5
        events_per_producer = 20

        def producer_worker(prod_id: int):
            for i in range(events_per_producer):
                # Distribute priorities 1 through 5
                p = (i % 5) + 1
                pq.enqueue(EmergencyEvent(
                    priority=p,
                    event_type=f"EVENT_P{p}",
                    payload={"producer": prod_id, "index": i}
                ))

        threads = []
        for i in range(num_producers):
            t = threading.Thread(target=producer_worker, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        expected_total = num_producers * events_per_producer
        assert pq.size() == expected_total

        # Drain queue and verify that priorities come out non-decreasing (1 <= 2 <= 3 <= 4 <= 5)
        drained_priorities = []
        while not pq.is_empty():
            ev = pq.dequeue(block=False)
            drained_priorities.append(ev.priority)

        assert len(drained_priorities) == expected_total
        for idx in range(len(drained_priorities) - 1):
            assert drained_priorities[idx] <= drained_priorities[idx + 1]
