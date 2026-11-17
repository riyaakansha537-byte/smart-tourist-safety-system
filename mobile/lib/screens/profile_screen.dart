// ============================================================
// Smart Tourist Safety and Emergency Response System
// Screen: Tourist Profile and Diagnostics
// ============================================================

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/app_theme.dart';
import '../config/api_config.dart';
import '../providers/app_state_provider.dart';
import '../widgets/glass_container.dart';

class ProfileScreen extends StatelessWidget {
  final bool showAppBar;

  const ProfileScreen({super.key, this.showAppBar = true});

  void _handleLogout(BuildContext context, AppStateProvider provider) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.bgSurface,
        title: const Text('Log Out Session'),
        content: const Text(
          'This will remove your saved tourist ID from this device and stop simulated telemetry pings. Continue?',
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
              await provider.logout();
              if (context.mounted) {
                Navigator.pushNamedAndRemoveUntil(
                  context,
                  '/register',
                  (route) => false,
                );
              }
            },
            child: const Text('Log Out'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<AppStateProvider>(context);
    final tourist = provider.tourist;

    final body = SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Tourist Safety Profile',
              style: TextStyle(
                color: AppTheme.textMain,
                fontSize: 20,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 2),
            const Text(
              'Digital Safety ID verified on Central Authority Network',
              style: TextStyle(
                color: AppTheme.textDim,
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 18),

            // Digital Safety ID Card
            GlassContainer(
              padding: const EdgeInsets.all(20),
              backgroundColor: AppTheme.bgCard,
              border: Border.all(
                color: AppTheme.primary.withOpacity(0.3),
                width: 1.5,
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
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              gradient: const LinearGradient(
                                colors: [AppTheme.primary, AppTheme.cyan],
                              ),
                            ),
                            child: const Icon(
                              Icons.verified_user_rounded,
                              color: Colors.white,
                              size: 24,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                tourist?.name ?? 'Registered Tourist',
                                style: const TextStyle(
                                  color: AppTheme.textMain,
                                  fontSize: 17,
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                              Text(
                                'ID: #${tourist?.touristId ?? "---"}',
                                style: const TextStyle(
                                  color: AppTheme.cyan,
                                  fontSize: 12,
                                  fontFamily: 'monospace',
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: AppTheme.danger.withOpacity(0.18),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: AppTheme.danger.withOpacity(0.4),
                          ),
                        ),
                        child: Text(
                          tourist?.bloodGroup ?? 'N/A',
                          style: const TextStyle(
                            color: AppTheme.danger,
                            fontWeight: FontWeight.w800,
                            fontSize: 13,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  const Divider(color: AppTheme.borderSubtle),
                  const SizedBox(height: 12),
                  _infoItem(Icons.phone_outlined, 'Phone', tourist?.phone ?? 'N/A'),
                  const SizedBox(height: 8),
                  _infoItem(Icons.email_outlined, 'Email', tourist?.email ?? 'N/A'),
                  const SizedBox(height: 8),
                  _infoItem(
                    Icons.flag_outlined,
                    'Nationality',
                    tourist?.nationality ?? 'Not specified',
                  ),
                  if (tourist?.registeredAt != null) ...[
                    const SizedBox(height: 8),
                    _infoItem(
                      Icons.calendar_today_outlined,
                      'Member Since',
                      tourist!.registeredAt!,
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Live Diagnostics Card
            const Text(
              'System Diagnostics',
              style: TextStyle(
                color: AppTheme.textMain,
                fontSize: 15,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 10),
            GlassContainer(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  _statusRow(
                    'REST Backend API',
                    ApiConfig.baseUrl,
                    true,
                  ),
                  const SizedBox(height: 10),
                  _statusRow(
                    'WebSocket Gateway',
                    ApiConfig.wsUrl,
                    provider.socketConnected,
                  ),
                  const SizedBox(height: 10),
                  _statusRow(
                    'Background GPS Simulation',
                    '${provider.currentLat.toStringAsFixed(4)}, ${provider.currentLng.toStringAsFixed(4)}',
                    true,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Log Out Button
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () => _handleLogout(context, provider),
                icon: const Icon(Icons.logout_rounded, color: AppTheme.danger, size: 18),
                label: const Text(
                  'Deregister & Log Out',
                  style: TextStyle(color: AppTheme.danger),
                ),
                style: OutlinedButton.styleFrom(
                  side: BorderSide(color: AppTheme.danger.withOpacity(0.5)),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );

    if (!showAppBar) return body;

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      appBar: AppBar(
        title: const Text('TOURIST PROFILE'),
        backgroundColor: AppTheme.bgSurface,
      ),
      body: body,
    );
  }

  Widget _infoItem(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, color: AppTheme.textDim, size: 16),
        const SizedBox(width: 10),
        Text(
          '$label: ',
          style: const TextStyle(color: AppTheme.textDim, fontSize: 13),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(
              color: AppTheme.textMain,
              fontWeight: FontWeight.w600,
              fontSize: 13,
            ),
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }

  Widget _statusRow(String title, String subtitle, bool isOnline) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                color: AppTheme.textMain,
                fontSize: 13,
                fontWeight: FontWeight.w600,
              ),
            ),
            Text(
              subtitle,
              style: const TextStyle(
                color: AppTheme.textDim,
                fontSize: 11,
              ),
            ),
          ],
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: (isOnline ? AppTheme.success : AppTheme.danger)
                .withOpacity(0.15),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            isOnline ? 'ONLINE' : 'OFFLINE',
            style: TextStyle(
              color: isOnline ? AppTheme.success : AppTheme.danger,
              fontSize: 10,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
      ],
    );
  }
}
