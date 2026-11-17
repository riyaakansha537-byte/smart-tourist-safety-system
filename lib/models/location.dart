// ============================================================
// Smart Tourist Safety and Emergency Response System
// Model: Location & Zone Telemetry
// ============================================================

class LocationModel {
  final int locationId;
  final int touristId;
  final double latitude;
  final double longitude;
  final String recordedAt;
  final int? zoneId;
  final Map<String, dynamic>? zone;

  static double _parseCoordinate(dynamic value, String fieldName) {
    if (value is num) return value.toDouble();
    if (value is String) {
      final parsed = double.tryParse(value);
      if (parsed != null) return parsed;
    }
    throw FormatException('Invalid $fieldName coordinate: $value');
  }

  LocationModel({
    required this.locationId,
    required this.touristId,
    required this.latitude,
    required this.longitude,
    required this.recordedAt,
    this.zoneId,
    this.zone,
  });

  factory LocationModel.fromJson(Map<String, dynamic> json) {
    return LocationModel(
      locationId: json['location_id'] as int,
      touristId: json['tourist_id'] as int,
      latitude: _parseCoordinate(json['latitude'], 'latitude'),
      longitude: _parseCoordinate(json['longitude'], 'longitude'),
      recordedAt: json['recorded_at']?.toString() ?? '',
      zoneId: json['zone_id'] as int?,
      zone: json['zone'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'location_id': locationId,
      'tourist_id': touristId,
      'latitude': latitude,
      'longitude': longitude,
      'recorded_at': recordedAt,
      'zone_id': zoneId,
      'zone': zone,
    };
  }

  bool get isInDangerousZone {
    if (zone == null) return false;
    return zone!['zone_type'] == 'DANGEROUS';
  }

  String get zoneName {
    if (zone == null) return 'Open Territory';
    return zone!['zone_name'] ?? 'Protected Area';
  }
}
