"""Unit tests for the database-independent safety system components."""

import unittest

from backend.resource_manager.bankers_algorithm import BankersAlgorithm
from backend.scheduler.priority_queue import EmergencyEvent, EmergencyPriorityQueue
from backend.utils.geofence import detect_primary_zone, haversine_distance_km
from backend.utils.validators import (
    validate_emergency_data,
    validate_location_data,
    validate_tourist_data,
)


class ValidatorTests(unittest.TestCase):
    def test_accepts_valid_tourist_registration(self):
        valid, errors = validate_tourist_data(
            {
                "name": "Asha Rao",
                "phone": "+91 98765 43210",
                "email": "asha@example.com",
                "blood_group": "o+",
            }
        )
        self.assertTrue(valid)
        self.assertEqual(errors, [])

    def test_rejects_invalid_location_ranges_and_boolean_coordinates(self):
        valid, errors = validate_location_data(
            {"tourist_id": True, "latitude": 91, "longitude": False}
        )
        self.assertFalse(valid)
        self.assertEqual(len(errors), 3)

    def test_emergency_defaults_are_applied(self):
        valid, errors = validate_emergency_data(
            {"tourist_id": 4, "latitude": 0, "longitude": 0},
            default_type="SOS",
            default_priority=2,
        )
        self.assertTrue(valid, errors)


class GeofenceTests(unittest.TestCase):
    def test_haversine_distance_at_same_coordinate_is_zero(self):
        self.assertEqual(haversine_distance_km(12.9, 77.6, 12.9, 77.6), 0.0)

    def test_dangerous_zone_takes_precedence_over_safe_zone(self):
        zones = [
            {"zone_id": 1, "zone_type": "SAFE", "risk_level": "LOW",
             "center_lat": 0, "center_lng": 0, "radius_km": 2},
            {"zone_id": 2, "zone_type": "DANGEROUS", "risk_level": "HIGH",
             "center_lat": 0, "center_lng": 0, "radius_km": 2},
        ]
        self.assertEqual(detect_primary_zone(0, 0, zones)["zone_id"], 2)


class PriorityQueueTests(unittest.TestCase):
    def test_dequeues_lowest_priority_number_first_and_keeps_fifo_ties(self):
        event_queue = EmergencyPriorityQueue()
        event_queue.enqueue(EmergencyEvent(priority=3, timestamp=1, event_id="first"))
        event_queue.enqueue(EmergencyEvent(priority=1, timestamp=5, event_id="urgent"))
        event_queue.enqueue(EmergencyEvent(priority=3, timestamp=1, event_id="second"))

        self.assertEqual(
            [event_queue.dequeue().event_id for _ in range(3)],
            ["urgent", "first", "second"],
        )


class BankersAlgorithmTests(unittest.TestCase):
    def test_safe_allocation_and_release_restore_available_resources(self):
        banker = BankersAlgorithm({"AMBULANCE": 2, "RESCUE_TEAM": 1, "HELICOPTER": 0})
        banker.register_process(7, {"AMBULANCE": 2, "RESCUE_TEAM": 1})

        granted, _, sequence = banker.request_resources(
            7, {"AMBULANCE": 1, "RESCUE_TEAM": 1}
        )
        self.assertTrue(granted)
        self.assertEqual(sequence, [7])
        self.assertEqual(banker.available["AMBULANCE"], 1)

        released, _ = banker.release_resources(
            7, {"AMBULANCE": 1, "RESCUE_TEAM": 1}
        )
        self.assertTrue(released)
        self.assertEqual(banker.available["AMBULANCE"], 2)
        self.assertEqual(banker.available["RESCUE_TEAM"], 1)

    def test_rejects_request_that_exceeds_registered_claim(self):
        banker = BankersAlgorithm({"AMBULANCE": 2})
        banker.register_process(9, {"AMBULANCE": 1})

        granted, message, sequence = banker.request_resources(9, {"AMBULANCE": 2})
        self.assertFalse(granted)
        self.assertIn("exceeded", message)
        self.assertIsNone(sequence)
        self.assertEqual(banker.available["AMBULANCE"], 2)


if __name__ == "__main__":
    unittest.main()
