// ============================================================
// Smart Tourist Safety and Emergency Response System
// Widget: Incident Card
// ============================================================

import 'package:flutter/material.dart';
import '../config/app_theme.dart';
import '../models/emergency.dart';
import 'glass_container.dart';
import 'status_badge.dart';

class IncidentCard extends StatelessWidget {
  final EmergencyIncident incident;
  final VoidCallback? onTap;

  const IncidentCard({
    super.key,
    required this.incident,
    this.onTap,
  });

  IconData _getTypeIcon(String type) {
    switch (type.toUpperCase()) {
      case 'SOS':
      case 'SOS_BEACON':
        return Icons.emergency_rounded;
      case 'ACCIDENT':
        return Icons.car_crash_rounded;
      case 'GEOFENCE':
      case 'GEOFENCE_BREACH':
        return Icons.fence_rounded;
      case 'MEDICAL':
        return Icons.medical_services_rounded;
      default:
        return Icons.warning_amber_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    return GlassContainer(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      onTap: onTap,
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
                      color: AppTheme.primary.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(
                      _getTypeIcon(incident.incidentType),
                      color: AppTheme.primaryLight,
                      size: 20,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Incident #${incident.incidentId}',
                        style: const TextStyle(
                          color: AppTheme.textMain,
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      Text(
                        incident.incidentType.replaceAll('_', ' '),
                        style: const TextStyle(
                          color: AppTheme.textDim,
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              StatusBadge(status: incident.status),
            ],
          ),
          const SizedBox(height: 12),
          if (incident.description != null &&
              incident.description!.trim().isNotEmpty) ...[
            Text(
              incident.description!,
              style: const TextStyle(
                color: AppTheme.textMuted,
                fontSize: 13,
                height: 1.4,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 10),
          ],
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(
                    Icons.location_on_outlined,
                    color: AppTheme.textDim,
                    size: 14,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '${incident.latitude.toStringAsFixed(3)}, ${incident.longitude.toStringAsFixed(3)}',
                    style: const TextStyle(
                      color: AppTheme.textDim,
                      fontSize: 12,
                      fontFamily: 'monospace',
                    ),
                  ),
                ],
              ),
              StatusBadge(
                status: incident.priority.toString(),
                isPriority: true,
              ),
            ],
          ),
          if (incident.createdAt.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(
              'Reported: ${incident.createdAt}',
              style: const TextStyle(
                color: AppTheme.textDim,
                fontSize: 11,
              ),
            ),
          ],
        ],
      ),
    );
  }
}
