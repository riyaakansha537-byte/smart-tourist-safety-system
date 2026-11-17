// ============================================================
// Smart Tourist Safety and Emergency Response System
// Screen: Emergency Incident History
// ============================================================

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/app_theme.dart';
import '../models/emergency.dart';
import '../providers/app_state_provider.dart';
import '../widgets/glass_container.dart';
import '../widgets/incident_card.dart';
import '../widgets/status_badge.dart';

class EmergencyHistoryScreen extends StatefulWidget {
  final bool showAppBar;

  const EmergencyHistoryScreen({super.key, this.showAppBar = true});

  @override
  State<EmergencyHistoryScreen> createState() => _EmergencyHistoryScreenState();
}

class _EmergencyHistoryScreenState extends State<EmergencyHistoryScreen> {
  String _filter = 'ALL';

  void _showIncidentDetail(BuildContext context, EmergencyIncident incident) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.bgSurface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(22),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Incident #${incident.incidentId}',
                  style: const TextStyle(
                    color: AppTheme.textMain,
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                StatusBadge(status: incident.status),
              ],
            ),
            const SizedBox(height: 14),
            const Divider(color: AppTheme.borderSubtle),
            const SizedBox(height: 10),
            _detailRow('Type', incident.incidentType.replaceAll('_', ' ')),
            _detailRow('Priority', 'Level ${incident.priority}'),
            _detailRow(
              'Coordinates',
              '${incident.latitude.toStringAsFixed(4)}°N, ${incident.longitude.toStringAsFixed(4)}°E',
            ),
            _detailRow('Reported At', incident.createdAt),
            if (incident.resolvedAt != null)
              _detailRow('Resolved At', incident.resolvedAt!),
            if (incident.description != null &&
                incident.description!.isNotEmpty) ...[
              const SizedBox(height: 8),
              const Text(
                'Description:',
                style: TextStyle(
                  color: AppTheme.textDim,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                incident.description!,
                style: const TextStyle(color: AppTheme.textMuted, fontSize: 13),
              ),
            ],
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('Close'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _detailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(color: AppTheme.textDim, fontSize: 13),
          ),
          Text(
            value,
            style: const TextStyle(
              color: AppTheme.textMain,
              fontWeight: FontWeight.w600,
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<AppStateProvider>(context);
    final emergencies = provider.emergencies;

    final filtered = emergencies.where((e) {
      if (_filter == 'ACTIVE') return e.isActive;
      if (_filter == 'RESOLVED') return e.status == 'RESOLVED';
      if (_filter == 'DISPATCHED') return e.status == 'DISPATCHED';
      return true;
    }).toList();

    final body = SafeArea(
      child: RefreshIndicator(
        onRefresh: () => provider.loadEmergencies(),
        color: AppTheme.primaryLight,
        backgroundColor: AppTheme.bgSurface,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Emergency Incident History',
                style: TextStyle(
                  color: AppTheme.textMain,
                  fontSize: 20,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 2),
              const Text(
                'Real-time log of SOS triggers and emergency dispatches',
                style: TextStyle(
                  color: AppTheme.textDim,
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 16),

              // Filter Chips
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: ['ALL', 'ACTIVE', 'DISPATCHED', 'RESOLVED'].map((f) {
                    final isSelected = _filter == f;
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: FilterChip(
                        selected: isSelected,
                        label: Text(f),
                        labelStyle: TextStyle(
                          color: isSelected ? Colors.white : AppTheme.textMuted,
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                        backgroundColor: AppTheme.bgCard,
                        selectedColor: AppTheme.primary,
                        checkmarkColor: Colors.white,
                        side: BorderSide(
                          color: isSelected
                              ? AppTheme.primary
                              : AppTheme.borderSubtle,
                        ),
                        onSelected: (_) => setState(() => _filter = f),
                      ),
                    );
                  }).toList(),
                ),
              ),
              const SizedBox(height: 16),

              if (filtered.isEmpty)
                GlassContainer(
                  padding: const EdgeInsets.symmetric(vertical: 40, horizontal: 20),
                  child: Center(
                    child: Column(
                      children: [
                        Icon(
                          Icons.check_circle_outline_rounded,
                          size: 48,
                          color: AppTheme.success.withOpacity(0.5),
                        ),
                        const SizedBox(height: 12),
                        const Text(
                          'No Incidents Logged',
                          style: TextStyle(
                            color: AppTheme.textMain,
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'Your safety status is clear. All emergency dispatches will appear here.',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: AppTheme.textMuted,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                )
              else
                ...filtered.map(
                  (inc) => IncidentCard(
                    incident: inc,
                    onTap: () => _showIncidentDetail(context, inc),
                  ),
                ),
            ],
          ),
        ),
      ),
    );

    if (!widget.showAppBar) return body;

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      appBar: AppBar(
        title: const Text('INCIDENT HISTORY'),
        backgroundColor: AppTheme.bgSurface,
      ),
      body: body,
    );
  }
}
