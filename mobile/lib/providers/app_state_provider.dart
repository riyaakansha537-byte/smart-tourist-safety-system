// ============================================================
// Smart Tourist Safety and Emergency Response System
// Provider: Application State Management
// ============================================================

import 'dart:async';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/tourist.dart';
import '../models/emergency_contact.dart';
import '../models/emergency.dart';
import '../models/notification.dart';
import '../services/api_service.dart';
import '../services/socket_service.dart';

class AppStateProvider extends ChangeNotifier {
  // Persisted tourist session
  Tourist? _tourist;
  int? _touristId;
  bool _isRegistered = false;
  bool _isLoading = false;
  String? _errorMessage;

  // Live data
  List<EmergencyContact> _contacts = [];
  List<EmergencyIncident> _emergencies = [];
  List<NotificationModel> _notifications = [];

  // Simulated GPS
  double _currentLat = 15.5553;
  double _currentLng = 73.7516;
  bool _isSendingLocation = false;
  bool _sosActive = false;
  String? _currentZoneName;
  bool _isInDangerZone = false;

  // Socket
  final SocketService _socketService = SocketService();
  bool _socketConnected = false;
  Timer? _locationTimer;

  // Getters
  Tourist? get tourist => _tourist;
  int? get touristId => _touristId;
  bool get isRegistered => _isRegistered;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  List<EmergencyContact> get contacts => _contacts;
  List<EmergencyIncident> get emergencies => _emergencies;
  List<NotificationModel> get notifications => _notifications;
  int get unreadCount => _notifications.where((n) => !n.isRead).length;
  double get currentLat => _currentLat;
  double get currentLng => _currentLng;
  bool get isSendingLocation => _isSendingLocation;
  bool get sosActive => _sosActive;
  String? get currentZoneName => _currentZoneName;
  bool get isInDangerZone => _isInDangerZone;
  bool get socketConnected => _socketConnected;

  // Initialize from persisted session
  Future<void> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    _touristId = prefs.getInt('tourist_id');
    if (_touristId != null) {
      _isRegistered = true;
      await _loadTouristProfile();
      _connectSocket();
      _startLocationSimulation();
    }
    notifyListeners();
  }

  // Register a new tourist
  Future<bool> register({
    required String name,
    required String phone,
    required String email,
    String? nationality,
    String? bloodGroup,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _tourist = await ApiService.registerTourist(
        name: name,
        phone: phone,
        email: email,
        nationality: nationality,
        bloodGroup: bloodGroup,
      );
      _touristId = _tourist!.touristId;
      _isRegistered = true;

      final prefs = await SharedPreferences.getInstance();
      await prefs.setInt('tourist_id', _touristId!);

      _connectSocket();
      _startLocationSimulation();

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Load tourist profile from backend
  Future<void> _loadTouristProfile() async {
    if (_touristId == null) return;
    try {
      _tourist = await ApiService.getTourist(_touristId!);
      await loadContacts();
      await loadEmergencies();
    } catch (e) {
      debugPrint('Error loading tourist profile: $e');
    }
  }

  // Load emergency contacts
  Future<void> loadContacts() async {
    if (_touristId == null) return;
    try {
      _contacts = await ApiService.getContacts(_touristId!);
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading contacts: $e');
    }
  }

  // Add emergency contact
  Future<bool> addContact({
    required String name,
    required String phone,
    required String relationship,
  }) async {
    if (_touristId == null) return false;
    _isLoading = true;
    notifyListeners();

    try {
      await ApiService.addContact(
        _touristId!,
        name: name,
        phone: phone,
        relationship: relationship,
      );
      await loadContacts();
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Delete emergency contact
  Future<bool> deleteContact(int contactId) async {
    if (_touristId == null) return false;
    try {
      final success = await ApiService.deleteContact(_touristId!, contactId);
      if (success) await loadContacts();
      return success;
    } catch (e) {
      return false;
    }
  }

  // Load emergencies
  Future<void> loadEmergencies() async {
    try {
      _emergencies = await ApiService.getEmergencies();
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading emergencies: $e');
    }
  }

  // Trigger SOS
  Future<bool> triggerSOS({String? description}) async {
    if (_touristId == null) return false;
    _sosActive = true;
    notifyListeners();

    try {
      final incident = await ApiService.triggerSOS(
        touristId: _touristId!,
        latitude: _currentLat,
        longitude: _currentLng,
        description: description,
      );

      _notifications.insert(
        0,
        NotificationModel(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          title: '🚨 SOS Sent!',
          message:
              'Emergency #${incident.incidentId} registered. Help is on the way.',
          type: 'ALERT',
          timestamp: DateTime.now(),
        ),
      );

      await loadEmergencies();
      _sosActive = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _sosActive = false;
      notifyListeners();
      return false;
    }
  }

  // Report accident
  Future<bool> reportAccident(String description) async {
    if (_touristId == null) return false;
    try {
      await ApiService.reportAccident(
        touristId: _touristId!,
        latitude: _currentLat,
        longitude: _currentLng,
        description: description,
      );
      await loadEmergencies();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  // Location simulation
  void _startLocationSimulation() {
    _locationTimer?.cancel();
    _locationTimer = Timer.periodic(const Duration(seconds: 10), (_) {
      _simulateLocationPing();
    });
  }

  Future<void> _simulateLocationPing() async {
    if (_touristId == null || _isSendingLocation) return;
    _isSendingLocation = true;

    // Simulate subtle movement
    final rng = Random();
    _currentLat += (rng.nextDouble() - 0.5) * 0.001;
    _currentLng += (rng.nextDouble() - 0.5) * 0.001;

    try {
      final result = await ApiService.submitLocation(
        touristId: _touristId!,
        latitude: _currentLat,
        longitude: _currentLng,
      );

      final zone = result['zone'] as Map<String, dynamic>?;
      if (zone != null) {
        _currentZoneName = zone['zone_name'] as String?;
        _isInDangerZone = zone['zone_type'] == 'DANGEROUS';
      } else {
        _currentZoneName = null;
        _isInDangerZone = false;
      }

      final bool geofenceBreach = result['geofence_breach'] == true;
      if (geofenceBreach) {
        _notifications.insert(
          0,
          NotificationModel(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            title: '⚠️ Dangerous Zone!',
            message: result['warning'] ?? 'You have entered a hazardous area.',
            type: 'WARNING',
            timestamp: DateTime.now(),
          ),
        );
      }
    } catch (e) {
      debugPrint('Location ping failed: $e');
    }

    _isSendingLocation = false;
    notifyListeners();
  }

  // Manually send location now
  Future<void> sendLocationNow() async {
    await _simulateLocationPing();
  }

  // Socket.IO connection
  void _connectSocket() {
    _socketService.onConnectionChanged = (connected) {
      _socketConnected = connected;
      notifyListeners();
    };

    _socketService.onNotification = (notification) {
      _notifications.insert(0, notification);
      notifyListeners();
    };

    _socketService.onEmergencyAlert = (data) {
      loadEmergencies();
    };

    _socketService.onStatusChanged = (data) {
      loadEmergencies();
    };

    _socketService.connect();
  }

  // Mark all notifications read
  void markAllNotificationsRead() {
    for (var n in _notifications) {
      n.isRead = true;
    }
    notifyListeners();
  }

  // Logout
  Future<void> logout() async {
    _locationTimer?.cancel();
    _socketService.disconnect();
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('tourist_id');
    _tourist = null;
    _touristId = null;
    _isRegistered = false;
    _contacts = [];
    _emergencies = [];
    _notifications = [];
    _sosActive = false;
    notifyListeners();
  }

  @override
  void dispose() {
    _locationTimer?.cancel();
    _socketService.disconnect();
    super.dispose();
  }
}
