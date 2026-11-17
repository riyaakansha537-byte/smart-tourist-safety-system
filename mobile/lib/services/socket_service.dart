// ============================================================
// Smart Tourist Safety and Emergency Response System
// Service: Socket.IO Real-Time Client
// ============================================================

import 'package:socket_io_client/socket_io_client.dart' as io;
import '../config/api_config.dart';
import '../models/notification.dart';

typedef EmergencyAlertCallback = void Function(Map<String, dynamic> data);
typedef StatusChangedCallback = void Function(Map<String, dynamic> data);

class SocketService {
  io.Socket? _socket;
  bool _isConnected = false;

  EmergencyAlertCallback? onEmergencyAlert;
  StatusChangedCallback? onStatusChanged;
  void Function(NotificationModel)? onNotification;
  void Function(bool)? onConnectionChanged;

  bool get isConnected => _isConnected;

  void connect() {
    _socket = io.io(
      ApiConfig.wsUrl,
      io.OptionBuilder()
          .setTransports(['websocket'])
          .disableAutoConnect()
          .enableReconnection()
          .setReconnectionDelay(2000)
          .build(),
    );

    _socket!.onConnect((_) {
      _isConnected = true;
      onConnectionChanged?.call(true);
      _socket!.emit('join_room', {'room': 'mobile'});
    });

    _socket!.onDisconnect((_) {
      _isConnected = false;
      onConnectionChanged?.call(false);
    });

    _socket!.on('emergency_alert', (data) {
      if (data is Map<String, dynamic>) {
        onEmergencyAlert?.call(data);

        final incident = data['incident'] as Map<String, dynamic>?;
        if (incident != null) {
          onNotification?.call(NotificationModel(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            title: '🚨 Emergency Alert',
            message:
                '${incident['incident_type']} (Priority ${incident['priority']}) reported!',
            type: 'ALERT',
            timestamp: DateTime.now(),
          ));
        }
      }
    });

    _socket!.on('incident_status_changed', (data) {
      if (data is Map<String, dynamic>) {
        onStatusChanged?.call(data);

        final incident = data['incident'] as Map<String, dynamic>?;
        if (incident != null) {
          onNotification?.call(NotificationModel(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            title: 'Status Update',
            message:
                'Incident #${incident['incident_id']} → ${incident['status']}',
            type: 'INFO',
            timestamp: DateTime.now(),
          ));
        }
      }
    });

    _socket!.on('resource_allocated', (data) {
      if (data is Map<String, dynamic>) {
        onNotification?.call(NotificationModel(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          title: '🚑 Resources Dispatched',
          message: 'Rescue team dispatched for incident #${data['incident_id']}',
          type: 'INFO',
          timestamp: DateTime.now(),
        ));
      }
    });

    _socket!.connect();
  }

  void disconnect() {
    _socket?.disconnect();
    _socket?.dispose();
    _socket = null;
    _isConnected = false;
  }
}
