// ============================================================
// Smart Tourist Safety and Emergency Response System
// Screen: Dedicated SOS Emergency Trigger
// ============================================================

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/app_theme.dart';
import '../providers/app_state_provider.dart';
import '../widgets/glass_container.dart';
import '../widgets/sos_button.dart';
import '../widgets/status_badge.dart';

class SOSScreen extends StatefulWidget {
  const SOSScreen({super.key});

  @override
  State<SOSScreen> createState() => _SOSScreenState();
}

class _SOSScreenState extends State<SOSScreen> {
  String _selectedType = 'SOS_BEACON';
  final _descriptionController = TextEditingController();
  bool _isDispatching = false;

  final List<Map<String, dynamic>> _incidentTypes = [
    {
      'type': 'SOS_BEACON',
      'label': 'SOS Beacon',
      'icon': Icons.emergency_rounded,
      'color': AppTheme.danger,
      'priority': 'P2',
      'desc': 'Immediate danger, unknown hazard, or distress signal',
    },
    {
      'type': 'MEDICAL',
      'label': 'Medical Emergency',
      'icon': Icons.medical_services_rounded,
      'color': Colors.redAccent,
      'priority': 'P1',
      'desc': 'Severe injury, cardiac event, or sudden illness',
    },
    {
      'type': 'ACCIDENT',
      'label': 'Road Accident',
      'icon': Icons.car_crash_rounded,
      'color': AppTheme.warning,
      'priority': 'P2',
      'desc': 'Vehicle collision, pedestrian incident, or road injury',
    },
    {
      'type': 'OCEAN_HAZARD',
      'label': 'Water / Drowning Hazard',
      'icon': Icons.water_damage_rounded,
      'color': AppTheme.cyan,
      'priority': 'P1',
      'desc': 'High tide drift, deep sea distress, rip currents',
    },
    {
      'type': 'LOST_GEOFENCE',
      'label': 'Lost in Restricted Area',
      'icon': Icons.explore_off_rounded,
      'color': AppTheme.purple,
      'priority': 'P3',
      'desc': 'Disoriented in cliffs, jungle, or hazardous terrain',
    },
  ];

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _triggerEmergency() async {
    setState(() => _isDispatching = true);
    final provider = Provider.of<AppStateProvider>(context, listen: false);

    final desc = _descriptionController.text.trim().isNotEmpty
        ? _descriptionController.text.trim()
        : 'Triggered emergency alert: $_selectedType';

    bool success;
    if (_selectedType == 'ACCIDENT') {
      success = await provider.reportAccident(desc);
    } else {
      success = await provider.triggerSOS(description: desc);
    }

    if (!mounted) return;
    setState(() => _isDispatching = false);

    if (success) {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (ctx) => AlertDialog(
          backgroundColor: AppTheme.bgSurface,
          title: const Row(
            children: [
              Icon(Icons.check_circle_rounded, color: AppTheme.success, size: 26),
              SizedBox(width: 10),
              Text('Alert Dispatched!'),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Your emergency signal was received by the Authority Emergency Command.',
                style: TextStyle(color: AppTheme.textMuted, fontSize: 13),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.bgCard,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: AppTheme.borderSubtle),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Type: ${_selectedType.replaceAll('_', ' ')}',
                      style: const TextStyle(
                        color: AppTheme.textMain,
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'GPS: ${provider.currentLat.toStringAsFixed(4)}°N, ${provider.currentLng.toStringAsFixed(4)}°E',
                      style: const TextStyle(
                        color: AppTheme.textDim,
                        fontSize: 12,
                        fontFamily: 'monospace',
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Status: DISPATCH QUEUED (Priority Queue)',
                      style: TextStyle(
                        color: AppTheme.warning,
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                Navigator.pop(ctx);
                Navigator.pop(context); // back to home
              },
              child: const Text('Return to Safety Center'),
            ),
          ],
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Failed to dispatch alert: ${provider.errorMessage ?? "Check network"}',
          ),
          backgroundColor: AppTheme.danger,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<AppStateProvider>(context);

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      appBar: AppBar(
        title: const Text('EMERGENCY SOS DISPATCH'),
        backgroundColor: AppTheme.bgSurface,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Notice banner
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.dangerDark.withOpacity(0.18),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppTheme.danger.withOpacity(0.4)),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.info_outline, color: AppTheme.danger, size: 20),
                    SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'Select the emergency category below to prioritize response resources.',
                        style: TextStyle(
                          color: AppTheme.textMain,
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Emergency Type selector
              const Text(
                'Select Incident Category',
                style: TextStyle(
                  color: AppTheme.textMain,
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 10),
              ..._incidentTypes.map((t) {
                final isSelected = _selectedType == t['type'];
                return GlassContainer(
                  margin: const EdgeInsets.only(bottom: 10),
                  padding: const EdgeInsets.all(14),
                  backgroundColor: isSelected
                      ? (t['color'] as Color).withOpacity(0.15)
                      : AppTheme.bgCard,
                  border: Border.all(
                    color: isSelected
                        ? (t['color'] as Color)
                        : AppTheme.borderSubtle,
                    width: isSelected ? 1.5 : 1.0,
                  ),
                  onTap: () => setState(() => _selectedType = t['type'] as String),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: (t['color'] as Color).withOpacity(0.15),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Icon(t['icon'] as IconData,
                            color: t['color'] as Color, size: 22),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Text(
                                  t['label'] as String,
                                  style: const TextStyle(
                                    color: AppTheme.textMain,
                                    fontSize: 14,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                                const SizedBox(width: 8),
                                StatusBadge(
                                  status: t['priority'] as String,
                                  isPriority: true,
                                ),
                              ],
                            ),
                            const SizedBox(height: 2),
                            Text(
                              t['desc'] as String,
                              style: const TextStyle(
                                color: AppTheme.textMuted,
                                fontSize: 11,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Radio<String>(
                        value: t['type'] as String,
                        groupValue: _selectedType,
                        activeColor: t['color'] as Color,
                        onChanged: (val) {
                          if (val != null) setState(() => _selectedType = val);
                        },
                      ),
                    ],
                  ),
                );
              }),
              const SizedBox(height: 16),

              // Description input
              const Text(
                'Situation Details (Optional)',
                style: TextStyle(
                  color: AppTheme.textMain,
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _descriptionController,
                maxLines: 2,
                style: const TextStyle(color: AppTheme.textMain, fontSize: 13),
                decoration: const InputDecoration(
                  hintText: 'What happened? e.g. suspected stroke, asthma attack, or injury',
                ),
              ),
              const SizedBox(height: 24),

              // Telemetry summary
              GlassContainer(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        const Icon(
                          Icons.gps_fixed_rounded,
                          color: AppTheme.cyan,
                          size: 16,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          '${provider.currentLat.toStringAsFixed(4)}°N, ${provider.currentLng.toStringAsFixed(4)}°E',
                          style: const TextStyle(
                            color: AppTheme.textMuted,
                            fontSize: 12,
                            fontFamily: 'monospace',
                          ),
                        ),
                      ],
                    ),
                    Text(
                      provider.currentZoneName ?? 'Open Area',
                      style: TextStyle(
                        color: provider.isInDangerZone
                            ? AppTheme.danger
                            : AppTheme.success,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 28),

              // SOS Trigger Button
              Center(
                child: SosButton(
                  size: 140,
                  isLoading: _isDispatching,
                  onPressed: _triggerEmergency,
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
