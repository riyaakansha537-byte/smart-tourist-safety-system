// ============================================================
// Smart Tourist Safety and Emergency Response System
// Screen: Main Dashboard (HomeScreen)
// ============================================================

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/app_theme.dart';
import '../providers/app_state_provider.dart';
import '../widgets/glass_container.dart';
import '../widgets/sos_button.dart';
import '../widgets/telemetry_card.dart';
import '../widgets/incident_card.dart';
import 'contacts_screen.dart';
import 'emergency_history_screen.dart';
import 'profile_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final List<Widget> pages = [
      const _HomeDashboardTab(),
      const EmergencyHistoryScreen(showAppBar: false),
      const ContactsScreen(showAppBar: false),
      const ProfileScreen(showAppBar: false),
    ];

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      body: IndexedStack(
        index: _currentIndex,
        children: pages,
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: AppTheme.bgSurface,
          border: const Border(
            top: BorderSide(color: AppTheme.borderSubtle, width: 1),
          ),
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (idx) => setState(() => _currentIndex = idx),
          backgroundColor: AppTheme.bgSurface,
          selectedItemColor: AppTheme.primaryLight,
          unselectedItemColor: AppTheme.textDim,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.shield_outlined),
              activeIcon: Icon(Icons.shield_rounded),
              label: 'Safety',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.history_toggle_off_rounded),
              activeIcon: Icon(Icons.history_rounded),
              label: 'History',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.contacts_outlined),
              activeIcon: Icon(Icons.contacts_rounded),
              label: 'Contacts',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_outline_rounded),
              activeIcon: Icon(Icons.person_rounded),
              label: 'Profile',
            ),
          ],
        ),
      ),
    );
  }
}

class _HomeDashboardTab extends StatelessWidget {
  const _HomeDashboardTab();

  void _showAccidentDialog(BuildContext context, AppStateProvider provider) {
    final textController = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.bgSurface,
        title: const Row(
          children: [
            Icon(Icons.car_crash_rounded, color: AppTheme.danger, size: 24),
            SizedBox(width: 8),
            Text('Report Accident'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Describe the incident or injuries for immediate rescue dispatch:',
              style: TextStyle(color: AppTheme.textMuted, fontSize: 13),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: textController,
              maxLines: 3,
              style: const TextStyle(color: AppTheme.textMain, fontSize: 14),
              decoration: const InputDecoration(
                hintText: 'e.g. Scooter skid near Baga beach road, minor injuries',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel', style: TextStyle(color: AppTheme.textDim)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.danger),
            onPressed: () async {
              final desc = textController.text.trim();
              if (desc.isEmpty) return;
              Navigator.pop(ctx);

              final ok = await provider.reportAccident(desc);
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(ok
                        ? 'Accident report dispatched to Authority Command!'
                        : 'Failed to report accident: ${provider.errorMessage}'),
                    backgroundColor: ok ? AppTheme.success : AppTheme.danger,
                  ),
                );
              }
            },
            child: const Text('Dispatch Report'),
          ),
        ],
      ),
    );
  }

  void _handleQuickSos(BuildContext context, AppStateProvider provider) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.bgSurface,
        title: const Row(
          children: [
            Icon(Icons.warning_amber_rounded, color: AppTheme.danger, size: 24),
            SizedBox(width: 8),
            Text('Confirm SOS Alert'),
          ],
        ),
        content: const Text(
          'This will trigger an immediate HIGH-PRIORITY beacon to emergency command and alert nearest rescue teams. Are you in immediate danger?',
          style: TextStyle(color: AppTheme.textMuted, fontSize: 13),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel', style: TextStyle(color: AppTheme.textDim)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.danger),
            onPressed: () async {
              Navigator.pop(ctx);
              final ok = await provider.triggerSOS(
                description: 'Instant mobile beacon triggered from Home Dashboard',
              );
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(ok
                        ? '🚨 SOS DISPATCHED: Rescue teams alerted!'
                        : 'Failed to send SOS: ${provider.errorMessage}'),
                    backgroundColor: ok ? AppTheme.danger : AppTheme.warning,
                  ),
                );
              }
            },
            child: const Text('SEND SOS NOW'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<AppStateProvider>(context);
    final tourist = provider.tourist;
    final activeEmergencies =
        provider.emergencies.where((e) => e.isActive).toList();

    return SafeArea(
      child: RefreshIndicator(
        onRefresh: () async {
          await provider.sendLocationNow();
          await provider.loadEmergencies();
        },
        color: AppTheme.primaryLight,
        backgroundColor: AppTheme.bgSurface,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Top Bar
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            tourist != null ? 'Hello, ${tourist.name}!' : 'Safety Shield',
                            style: const TextStyle(
                              color: AppTheme.textMain,
                              fontSize: 20,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          const SizedBox(width: 6),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 6,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: AppTheme.success.withOpacity(0.15),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: const Text(
                              'PROTECTED',
                              style: TextStyle(
                                color: AppTheme.success,
                                fontSize: 9,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 2),
                      Text(
                        tourist != null ? 'ID #${tourist.touristId} • ${tourist.bloodGroup ?? "N/A"}' : 'Safe Tourist Network',
                        style: const TextStyle(
                          color: AppTheme.textDim,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                  Stack(
                    children: [
                      IconButton(
                        onPressed: () {
                          Navigator.pushNamed(context, '/notifications');
                        },
                        icon: const Icon(
                          Icons.notifications_outlined,
                          color: AppTheme.textMain,
                          size: 24,
                        ),
                      ),
                      if (provider.unreadCount > 0)
                        Positioned(
                          right: 8,
                          top: 8,
                          child: Container(
                            padding: const EdgeInsets.all(4),
                            decoration: const BoxDecoration(
                              color: AppTheme.danger,
                              shape: BoxShape.circle,
                            ),
                            child: Text(
                              '${provider.unreadCount}',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 9,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 20),

              // SOS Center Piece Card
              GlassContainer(
                padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
                child: Column(
                  children: [
                    const Text(
                      'EMERGENCY SOS BEACON',
                      style: TextStyle(
                        color: AppTheme.textMain,
                        fontSize: 14,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.2,
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Tap to trigger immediate priority dispatch',
                      style: TextStyle(
                        color: AppTheme.textMuted,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(height: 20),
                    Center(
                      child: SosButton(
                        size: 130,
                        isLoading: provider.sosActive,
                        onPressed: () => _handleQuickSos(context, provider),
                      ),
                    ),
                    const SizedBox(height: 16),
                    OutlinedButton.icon(
                      onPressed: () {
                        Navigator.pushNamed(context, '/sos');
                      },
                      icon: const Icon(Icons.settings_input_antenna, size: 16),
                      label: const Text('Detailed SOS & Incident Types'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 18),

              // Telemetry Card
              TelemetryCard(
                latitude: provider.currentLat,
                longitude: provider.currentLng,
                zoneName: provider.currentZoneName,
                isInDangerZone: provider.isInDangerZone,
                isSendingLocation: provider.isSendingLocation,
                socketConnected: provider.socketConnected,
                onPingLocation: () => provider.sendLocationNow(),
              ),
              const SizedBox(height: 18),

              // Quick Action Grid
              const Text(
                'Safety Quick Actions',
                style: TextStyle(
                  color: AppTheme.textMain,
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: _QuickActionButton(
                      icon: Icons.car_crash_rounded,
                      iconColor: AppTheme.warning,
                      label: 'Report Accident',
                      subtitle: 'Collision or injuries',
                      onTap: () => _showAccidentDialog(context, provider),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _QuickActionButton(
                      icon: Icons.security_rounded,
                      iconColor: AppTheme.cyan,
                      label: 'SOS Protocol',
                      subtitle: 'Multi-hazard alert',
                      onTap: () => Navigator.pushNamed(context, '/sos'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _QuickActionButton(
                      icon: Icons.contact_emergency_rounded,
                      iconColor: AppTheme.primaryLight,
                      label: 'Contacts',
                      subtitle: '${provider.contacts.length} saved contacts',
                      onTap: () => Navigator.pushNamed(context, '/contacts'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _QuickActionButton(
                      icon: Icons.receipt_long_rounded,
                      iconColor: AppTheme.purple,
                      label: 'History',
                      subtitle: '${provider.emergencies.length} logged events',
                      onTap: () => Navigator.pushNamed(context, '/history'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 22),

              // Active incidents section if any
              if (activeEmergencies.isNotEmpty) ...[
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Active Incidents',
                      style: TextStyle(
                        color: AppTheme.textMain,
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    Text(
                      '${activeEmergencies.length} Ongoing',
                      style: const TextStyle(
                        color: AppTheme.danger,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                ...activeEmergencies.take(2).map(
                      (e) => IncidentCard(incident: e),
                    ),
                const SizedBox(height: 12),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _QuickActionButton extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String label;
  final String subtitle;
  final VoidCallback onTap;

  const _QuickActionButton({
    required this.icon,
    required this.iconColor,
    required this.label,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GlassContainer(
      padding: const EdgeInsets.all(14),
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: iconColor.withOpacity(0.12),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: iconColor, size: 20),
          ),
          const SizedBox(height: 10),
          Text(
            label,
            style: const TextStyle(
              color: AppTheme.textMain,
              fontSize: 13,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            subtitle,
            style: const TextStyle(
              color: AppTheme.textDim,
              fontSize: 11,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}
