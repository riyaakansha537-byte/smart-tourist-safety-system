// ============================================================
// Smart Tourist Safety and Emergency Response System
// Service: REST API Client
// ============================================================

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/tourist.dart';
import '../models/emergency_contact.dart';
import '../models/emergency.dart';

class ApiService {
  // 1. Tourist Registration
  static Future<Tourist> registerTourist({
    required String name,
    required String phone,
    required String email,
    String? nationality,
    String? bloodGroup,
  }) async {
    final response = await http.post(
      Uri.parse(ApiConfig.tourists),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': name,
        'phone': phone,
        'email': email,
        'nationality': nationality,
        'blood_group': bloodGroup,
      }),
    );

    final data = jsonDecode(response.body);
    if (response.statusCode == 201) {
      return Tourist.fromJson(data['data']);
    } else {
      throw Exception(data['message'] ?? 'Failed to register tourist');
    }
  }

  // 2. Fetch Tourist Profile
  static Future<Tourist?> getTourist(int touristId) async {
    final response = await http.get(Uri.parse('${ApiConfig.tourists}/$touristId'));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return Tourist.fromJson(data['data']);
    }
    return null;
  }

  // 3. Emergency Contacts
  static Future<EmergencyContact> addContact(
    int touristId, {
    required String name,
    required String phone,
    required String relationship,
  }) async {
    final response = await http.post(
      Uri.parse(ApiConfig.touristContacts(touristId)),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': name,
        'phone': phone,
        'relationship': relationship,
      }),
    );

    final data = jsonDecode(response.body);
    if (response.statusCode == 201) {
      return EmergencyContact.fromJson(data['data']);
    } else {
      throw Exception(data['message'] ?? 'Failed to add contact');
    }
  }

  static Future<List<EmergencyContact>> getContacts(int touristId) async {
    final response = await http.get(Uri.parse(ApiConfig.touristContacts(touristId)));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final list = data['data'] as List;
      return list.map((c) => EmergencyContact.fromJson(c)).toList();
    }
    return [];
  }

  static Future<bool> deleteContact(int touristId, int contactId) async {
    final response = await http.delete(
      Uri.parse('${ApiConfig.touristContacts(touristId)}/$contactId'),
    );
    return response.statusCode == 200;
  }

  // 4. GPS Location Submission
  static Future<Map<String, dynamic>> submitLocation({
    required int touristId,
    required double latitude,
    required double longitude,
  }) async {
    final response = await http.post(
      Uri.parse(ApiConfig.location),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'tourist_id': touristId,
        'latitude': latitude,
        'longitude': longitude,
      }),
    );

    final data = jsonDecode(response.body);
    if (response.statusCode == 201) {
      return data;
    } else {
      throw Exception(data['message'] ?? 'Failed to submit location');
    }
  }

  // 5. Emergency Incident Triggers
  static Future<EmergencyIncident> triggerSOS({
    required int touristId,
    required double latitude,
    required double longitude,
    String? description,
  }) async {
    final response = await http.post(
      Uri.parse(ApiConfig.reportSos),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'tourist_id': touristId,
        'latitude': latitude,
        'longitude': longitude,
        'description': description ?? 'SOS beacon triggered from mobile app',
      }),
    );

    final data = jsonDecode(response.body);
    if (response.statusCode == 201) {
      return EmergencyIncident.fromJson(data['data']);
    } else {
      throw Exception(data['message'] ?? 'Failed to trigger SOS');
    }
  }

  static Future<EmergencyIncident> reportAccident({
    required int touristId,
    required double latitude,
    required double longitude,
    required String description,
  }) async {
    final response = await http.post(
      Uri.parse(ApiConfig.reportAccident),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'tourist_id': touristId,
        'latitude': latitude,
        'longitude': longitude,
        'description': description,
      }),
    );

    final data = jsonDecode(response.body);
    if (response.statusCode == 201) {
      return EmergencyIncident.fromJson(data['data']);
    } else {
      throw Exception(data['message'] ?? 'Failed to report accident');
    }
  }

  // 6. Emergency History
  static Future<List<EmergencyIncident>> getEmergencies({
    String? status,
    int limit = 50,
    int offset = 0,
  }) async {
    String url = '${ApiConfig.emergencies}?limit=$limit&offset=$offset';
    if (status != null) url += '&status=$status';

    final response = await http.get(Uri.parse(url));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final list = data['data'] as List;
      return list.map((e) => EmergencyIncident.fromJson(e)).toList();
    }
    return [];
  }

  // 7. Get Active Zones
  static Future<List<Map<String, dynamic>>> getZones() async {
    final response = await http.get(Uri.parse(ApiConfig.getZones));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final list = data['data'] as List;
      return list.cast<Map<String, dynamic>>();
    }
    return [];
  }

  // 8. Health Check
  static Future<bool> checkHealth() async {
    try {
      final response = await http.get(Uri.parse(ApiConfig.health)).timeout(
        const Duration(seconds: 5),
      );
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
