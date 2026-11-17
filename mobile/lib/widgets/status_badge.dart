// ============================================================
// Smart Tourist Safety and Emergency Response System
// Widget: Status and Priority Badge
// ============================================================

import 'package:flutter/material.dart';
import '../config/app_theme.dart';

class StatusBadge extends StatelessWidget {
  final String status;
  final bool isPriority;

  const StatusBadge({
    super.key,
    required this.status,
    this.isPriority = false,
  });

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color fg;
    IconData icon;

    final normalized = status.toUpperCase().trim();

    if (isPriority) {
      switch (normalized) {
        case '1':
        case 'P1':
        case 'CRITICAL':
          bg = AppTheme.danger.withOpacity(0.2);
          fg = AppTheme.danger;
          icon = Icons.priority_high;
          break;
        case '2':
        case 'P2':
        case 'SOS':
          bg = Colors.deepOrange.withOpacity(0.2);
          fg = Colors.deepOrangeAccent;
          icon = Icons.warning_amber_rounded;
          break;
        case '3':
        case 'P3':
        case 'GEOFENCE':
        case 'ZONE':
          bg = AppTheme.warning.withOpacity(0.2);
          fg = AppTheme.warning;
          icon = Icons.location_off_rounded;
          break;
        case '4':
        case 'P4':
        case 'ALERT':
          bg = AppTheme.primary.withOpacity(0.2);
          fg = AppTheme.primaryLight;
          icon = Icons.notifications_active;
          break;
        default:
          bg = AppTheme.textDim.withOpacity(0.2);
          fg = AppTheme.textMuted;
          icon = Icons.info_outline;
          break;
      }
    } else {
      switch (normalized) {
        case 'RESOLVED':
          bg = AppTheme.success.withOpacity(0.2);
          fg = AppTheme.success;
          icon = Icons.check_circle_outline;
          break;
        case 'DISPATCHED':
        case 'IN_PROGRESS':
          bg = AppTheme.cyan.withOpacity(0.2);
          fg = AppTheme.cyan;
          icon = Icons.local_shipping_outlined;
          break;
        case 'REPORTED':
        case 'PENDING':
          bg = AppTheme.warning.withOpacity(0.2);
          fg = AppTheme.warning;
          icon = Icons.hourglass_top_rounded;
          break;
        case 'FAILED':
        case 'CANCELLED':
          bg = AppTheme.danger.withOpacity(0.2);
          fg = AppTheme.danger;
          icon = Icons.error_outline;
          break;
        default:
          bg = AppTheme.primary.withOpacity(0.2);
          fg = AppTheme.primaryLight;
          icon = Icons.circle;
          break;
      }
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: fg.withOpacity(0.4), width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: fg),
          const SizedBox(width: 5),
          Text(
            isPriority ? 'P$status' : status,
            style: TextStyle(
              color: fg,
              fontSize: 11,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }
}
