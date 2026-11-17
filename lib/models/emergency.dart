// ============================================================
// Smart Tourist Safety and Emergency Response System
// Model: Emergency Incident
// ============================================================

class EmergencyIncident {
  final int incidentId;
  final int touristId;
  final String incidentType;
  final int priority;
  final String status;
  final double latitude;
  final double longitude;
  final String? description;
  final String createdAt;
  final String? resolvedAt;

  static double _parseCoordinate(dynamic value, String fieldName) {
    if (value is num) return value.toDouble();
    if (value is String) {
      final parsed = double.tryParse(value);
      if (parsed != null) return parsed;
    }
    throw FormatException('Invalid $fieldName coordinate: $value');
  }

  EmergencyIncident({
    required this.incidentId,
    required this.touristId,
    required this.incidentType,
    required this.priority,
    required this.status,
    required this.latitude,
    required this.longitude,
    this.description,
    required this.createdAt,
    this.resolvedAt,
  });

  factory EmergencyIncident.fromJson(Map<String, dynamic> json) {
    return EmergencyIncident(
      incidentId: json['incident_id'] as int,
      touristId: json['tourist_id'] as int,
      incidentType: json['incident_type'] as String,
      priority: json['priority'] as int,
      status: json['status'] as String,
      latitude: _parseCoordinate(json['latitude'], 'latitude'),
      longitude: _parseCoordinate(json['longitude'], 'longitude'),
      description: json['description'] as String?,
      createdAt: json['created_at']?.toString() ?? '',
      resolvedAt: json['resolved_at']?.toString(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'incident_id': incidentId,
      'tourist_id': touristId,
      'incident_type': incidentType,
      'priority': priority,
      'status': status,
      'latitude': latitude,
      'longitude': longitude,
      'description': description,
      'created_at': createdAt,
      'resolved_at': resolvedAt,
    };
  }

  bool get isActive => status != 'RESOLVED' && status != 'FAILED';
}
