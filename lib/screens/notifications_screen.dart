// ============================================================
// Smart Tourist Safety and Emergency Response System
// Screen: Safety Alerts and Notifications
// ============================================================

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/app_theme.dart';
import '../models/notification.dart';
import '../providers/app_state_provider.dart';
import '../widgets/glass_container.dart';

class NotificationsScreen extends StatelessWidget {
  const NotificationsScreen({super.key});

  IconData _getIcon(String type) {
    switch (type.toUpperCase()) {
      case 'ALERT':
        return Icons.emergency_rounded;
      case 'WARNING':
        return Icons.warning_amber_rounded;
      case 'INFO':
      default:
        return Icons.notifications_active_rounded;
    }
  }

  Color _getColor(String type) {
    switch (type.toUpperCase()) {
      case 'ALERT':
        return AppTheme.danger;
      case 'WARNING':
        return AppTheme.warning;
      case 'INFO':
      default:
        return AppTheme.cyan;
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<AppStateProvider>(context);
    final notifications = provider.notifications;

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      appBar: AppBar(
        title: const Text('SAFETY ALERTS'),
        backgroundColor: AppTheme.bgSurface,
        actions: [
          if (notifications.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.done_all_rounded, color: AppTheme.textMuted),
              tooltip: 'Mark all as read',
              onPressed: () => provider.markAllNotificationsRead(),
            ),
        ],
      ),
      body: SafeArea(
        child: notifications.isEmpty
            ? Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.notifications_off_outlined,
                      size: 54,
                      color: AppTheme.textDim.withOpacity(0.5),
                    ),
                    const SizedBox(height: 14),
                    const Text(
                      'No Active Alerts',
                      style: TextStyle(
                        color: AppTheme.textMain,
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      'Geofence alerts and dispatch updates will appear here.',
                      style: TextStyle(
                        color: AppTheme.textMuted,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              )
            : ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
                itemCount: notifications.length,
                itemBuilder: (context, index) {
                  final notif = notifications[index];
                  final color = _getColor(notif.type);

                  return GlassContainer(
                    margin: const EdgeInsets.only(bottom: 10),
                    padding: const EdgeInsets.all(14),
                    backgroundColor: notif.isRead
                        ? AppTheme.bgCard
                        : color.withOpacity(0.12),
                    border: Border.all(
                      color: notif.isRead
                          ? AppTheme.borderSubtle
                          : color.withOpacity(0.4),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: color.withOpacity(0.15),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Icon(_getIcon(notif.type), color: color, size: 20),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(
                                    notif.title,
                                    style: const TextStyle(
                                      color: AppTheme.textMain,
                                      fontSize: 14,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                  Text(
                                    '${notif.timestamp.hour.toString().padLeft(2, '0')}:${notif.timestamp.minute.toString().padLeft(2, '0')}',
                                    style: const TextStyle(
                                      color: AppTheme.textDim,
                                      fontSize: 11,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 4),
                              Text(
                                notif.message,
                                style: const TextStyle(
                                  color: AppTheme.textMuted,
                                  fontSize: 13,
                                  height: 1.3,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
      ),
    );
  }
}
