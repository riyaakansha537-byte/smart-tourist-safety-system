# ============================================================
# Smart Tourist Safety and Emergency Response System
# Input Validation Utilities
# ============================================================

import re
from typing import Any, Dict, List, Optional, Tuple

VALID_BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-()]{7,25}$")

def validate_tourist_data(
    data: Optional[Dict[str, Any]], 
    is_update: bool = False
) -> Tuple[bool, List[str]]:
    """
    Validates tourist registration or update payload.
    Returns (is_valid, list_of_error_messages).
    """
    errors: List[str] = []
    if not isinstance(data, dict):
        return False, ["Request body must be a valid JSON object."]

    name = data.get("name")
    phone = data.get("phone")
    email = data.get("email")
    blood_group = data.get("blood_group")

    if not is_update:
        if not name or not isinstance(name, str) or len(name.strip()) < 2:
            errors.append("Field 'name' is required and must be at least 2 characters.")
        if not phone or not isinstance(phone, str) or not PHONE_REGEX.match(phone.strip()):
            errors.append("Field 'phone' is required and must be a valid telephone format.")
        if not email or not isinstance(email, str) or not EMAIL_REGEX.match(email.strip()):
            errors.append("Field 'email' is required and must be a valid email address.")
    else:
        if name is not None:
            if not isinstance(name, str) or len(name.strip()) < 2:
                errors.append("Field 'name' must be at least 2 characters.")
        if phone is not None:
            if not isinstance(phone, str) or not PHONE_REGEX.match(phone.strip()):
                errors.append("Field 'phone' must be a valid telephone format.")
        if email is not None:
            if not isinstance(email, str) or not EMAIL_REGEX.match(email.strip()):
                errors.append("Field 'email' must be a valid email address.")

    if blood_group is not None:
        if isinstance(blood_group, str):
            clean_bg = blood_group.strip().upper()
            if clean_bg and clean_bg not in VALID_BLOOD_GROUPS:
                errors.append(f"Invalid 'blood_group'. Allowed values: {', '.join(sorted(VALID_BLOOD_GROUPS))}.")
        else:
            errors.append("'blood_group' must be a string.")

    return len(errors) == 0, errors

def validate_contact_data(data: Optional[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validates emergency contact payload.
    Returns (is_valid, list_of_error_messages).
    """
    errors: List[str] = []
    if not isinstance(data, dict):
        return False, ["Request body must be a valid JSON object."]

    name = data.get("name")
    phone = data.get("phone")
    relationship = data.get("relationship")

    if not name or not isinstance(name, str) or len(name.strip()) < 2:
        errors.append("Field 'name' is required and must be at least 2 characters.")
    if not phone or not isinstance(phone, str) or not PHONE_REGEX.match(phone.strip()):
        errors.append("Field 'phone' is required and must be a valid telephone format.")
    if not relationship or not isinstance(relationship, str) or len(relationship.strip()) < 2:
        errors.append("Field 'relationship' is required (e.g. 'Spouse', 'Parent', 'Friend').")

    return len(errors) == 0, errors

def validate_location_data(data: Optional[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validates GPS telemetry location update payload.
    Returns (is_valid, list_of_error_messages).
    """
    errors: List[str] = []
    if not isinstance(data, dict):
        return False, ["Request body must be a valid JSON object."]

    tourist_id = data.get("tourist_id")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if tourist_id is None:
        errors.append("Field 'tourist_id' is required.")
    elif isinstance(tourist_id, bool) or not isinstance(tourist_id, int) or tourist_id <= 0:
        errors.append("Field 'tourist_id' must be a positive integer.")

    if latitude is None:
        errors.append("Field 'latitude' is required.")
    elif isinstance(latitude, bool) or not isinstance(latitude, (int, float)):
        errors.append("Field 'latitude' must be a numeric value.")
    elif not (-90.0 <= float(latitude) <= 90.0):
        errors.append("Field 'latitude' must be between -90.0 and 90.0 degrees.")

    if longitude is None:
        errors.append("Field 'longitude' is required.")
    elif isinstance(longitude, bool) or not isinstance(longitude, (int, float)):
        errors.append("Field 'longitude' must be a numeric value.")
    elif not (-180.0 <= float(longitude) <= 180.0):
        errors.append("Field 'longitude' must be between -180.0 and 180.0 degrees.")

    return len(errors) == 0, errors

VALID_INCIDENT_TYPES = {
    "CRITICAL_ACCIDENT",
    "SOS",
    "DANGEROUS_ZONE",
    "SAFETY_ALERT",
    "GPS_UPDATE",
}

VALID_INCIDENT_STATUSES = {
    "RECEIVED",
    "QUEUED",
    "PROCESSING",
    "RESOURCE_ASSIGNED",
    "RESOLVED",
    "FAILED",
}

def validate_emergency_data(
    data: Optional[Dict[str, Any]],
    default_type: Optional[str] = None,
    default_priority: Optional[int] = None,
) -> Tuple[bool, List[str]]:
    """
    Validates emergency incident report payload.
    Returns (is_valid, list_of_error_messages).
    """
    errors: List[str] = []
    if not isinstance(data, dict):
        return False, ["Request body must be a valid JSON object."]

    tourist_id = data.get("tourist_id")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    incident_type = data.get("incident_type", default_type)
    priority = data.get("priority", default_priority)
    description = data.get("description")

    if tourist_id is None:
        errors.append("Field 'tourist_id' is required.")
    elif isinstance(tourist_id, bool) or not isinstance(tourist_id, int) or tourist_id <= 0:
        errors.append("Field 'tourist_id' must be a positive integer.")

    if latitude is None:
        errors.append("Field 'latitude' is required.")
    elif isinstance(latitude, bool) or not isinstance(latitude, (int, float)):
        errors.append("Field 'latitude' must be a numeric value.")
    elif not (-90.0 <= float(latitude) <= 90.0):
        errors.append("Field 'latitude' must be between -90.0 and 90.0 degrees.")

    if longitude is None:
        errors.append("Field 'longitude' is required.")
    elif isinstance(longitude, bool) or not isinstance(longitude, (int, float)):
        errors.append("Field 'longitude' must be a numeric value.")
    elif not (-180.0 <= float(longitude) <= 180.0):
        errors.append("Field 'longitude' must be between -180.0 and 180.0 degrees.")

    if not incident_type or incident_type not in VALID_INCIDENT_TYPES:
        errors.append(
            f"Invalid 'incident_type'. Allowed values: {', '.join(sorted(VALID_INCIDENT_TYPES))}."
        )

    if priority is None:
        errors.append("Field 'priority' is required.")
    elif isinstance(priority, bool) or not isinstance(priority, int) or not (1 <= priority <= 5):
        errors.append("Field 'priority' must be an integer between 1 (highest) and 5 (lowest).")

    if description is not None and not isinstance(description, str):
        errors.append("Field 'description' must be a text string.")

    return len(errors) == 0, errors

def validate_status_update_data(data: Optional[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validates incident status update payload.
    """
    errors: List[str] = []
    if not isinstance(data, dict):
        return False, ["Request body must be a valid JSON object."]

    status = data.get("status")
    if not status or not isinstance(status, str) or status.strip() not in VALID_INCIDENT_STATUSES:
        errors.append(
            f"Invalid or missing 'status'. Allowed values: {', '.join(sorted(VALID_INCIDENT_STATUSES))}."
        )

    return len(errors) == 0, errors
