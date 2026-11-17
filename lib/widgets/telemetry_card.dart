// ============================================================
// Smart Tourist Safety and Emergency Response System
// Widget: Real-Time Telemetry and Geofence Status Card
// ============================================================

import 'package:flutter/material.dart';
import '../config/app_theme.dart';
import 'glass_container.dart';

class TelemetryCard extends StatelessWidget {
  final double latitude;
  final double longitude;
  final String? zoneName;
  final bool isInDangerZone;
  final bool isSendingLocation;
  final bool socketConnected;
  final VoidCallback onPingLocation;

  const TelemetryCard({
    super.key,
    required this.latitude,
    required this.longitude,
    required this.zoneName,
    required this.isInDangerZone,
    required this.isSendingLocation,
    required this.socketConnected,
    required this.onPingLocation,
  });

  @override
  Widget build(BuildContext context) {
    return GlassContainer(
      padding: const EdgeInsets.all(18),
      backgroundColor: isInDangerZone
          ? AppTheme.dangerDark.withOpacity(0.18)
          : AppTheme.bgCard,
      border: Border.all(
        color: isInDangerZone
            ? AppTheme.danger.withOpacity(0.4)
            : AppTheme.borderSubtle,
        width: isInDangerZone ? 1.5 : 1.0,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: (isInDangerZone ? AppTheme.danger : AppTheme.primary)
                          .withOpacity(0.15),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(
                      isInDangerZone
                          ? Icons.warning_amber_rounded
                          : Icons.my_location_rounded,
                      color: isInDangerZone ? AppTheme.danger : AppTheme.primary,
                      size: 20,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Live GPS Telemetry',
                        style: TextStyle(
                          color: AppTheme.textMain,
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      Row(
                        children: [
                          Container(
                            width: 7,
                            height: 7,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: socketConnected
                                  ? AppTheme.success
                                  : AppTheme.warning,
                            ),
                          ),
                          const SizedBox(width: 5),
                          Text(
                            socketConnected
                                ? 'Real-Time Sync Active'
                                : 'Connecting socket...',
                            style: TextStyle(
                              color: socketConnected
                                  ? AppTheme.success
                                  : AppTheme.warning,
                              fontSize: 11,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ],
              ),
              IconButton(
                onPressed: isSendingLocation ? null : onPingLocation,
                icon: isSendingLocation
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: AppTheme.cyan,
                        ),
                      )
                    : const Icon(
                        Icons.refresh_rounded,
                        color: AppTheme.cyan,
                        size: 22,
                      ),
                tooltip: 'Ping Location Now',
              ),
            ],
          ),
          const SizedBox(height: 14),
          const Divider(color: AppTheme.borderSubtle),
          const SizedBox(height: 10),

          // Zone banner
          if (isInDangerZone)
            Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: AppTheme.danger.withOpacity(0.15),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: AppTheme.danger.withOpacity(0.5),
                  width: 1,
                ),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.dangerous_outlined,
                    color: AppTheme.danger,
                    size: 18,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'ALERT: Inside Restricted / Dangerous Zone',
                      style: const TextStyle(
                        color: AppTheme.danger,
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ],
              ),
            ),

          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'COORDINATES',
                      style: TextStyle(
                        color: AppTheme.textDim,
                        fontSize: 10,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '${latitude.toStringAsFixed(4)}°N, ${longitude.toStringAsFixed(4)}°E',
                      style: const TextStyle(
                        color: AppTheme.textMain,
                        fontSize: 13,
                        fontFamily: 'monospace',
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'CURRENT ZONE',
                      style: TextStyle(
                        color: AppTheme.textDim,
                        fontSize: 10,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      zoneName ?? 'Open Safe Territory',
                      style: TextStyle(
                        color: isInDangerZone
                            ? AppTheme.danger
                            : AppTheme.success,
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
