// ============================================================
// Smart Tourist Safety and Emergency Response System
// Flutter Client API Configuration
// ============================================================

class ApiConfig {
  // Base URL: http://127.0.0.1:5000 works for:
  // 1. Android physical device connected via USB with `adb reverse tcp:5000 tcp:5000`
  // 2. Web browser (Chrome) / Desktop
  // Note: For Android Studio emulator without adb reverse, use http://10.0.2.2:5000
  static const String baseUrl = 'http://127.0.0.1:5000';
  static const String wsUrl = 'http://127.0.0.1:5000';

  // Endpoints
  static const String health = '$baseUrl/api/health';
  static const String tourists = '$baseUrl/api/tourists';
  static const String location = '$baseUrl/api/location';
  static const String emergencies = '$baseUrl/api/emergencies';
  static const String resources = '$baseUrl/api/resources';
  static const String dashboard = '$baseUrl/api/dashboard';

  // Specific Actions
  static String touristContacts(int touristId) => '$tourists/$touristId/contacts';
  static String touristLocations(int touristId) => '$tourists/$touristId/locations';
  static const String reportAccident = '$emergencies/accident';
  static const String reportSos = '$emergencies/sos';
  static const String reportGeofence = '$emergencies/geofence';
  static const String reportAlert = '$emergencies/safety-alert';
  static const String getZones = '$location/zones';
}
