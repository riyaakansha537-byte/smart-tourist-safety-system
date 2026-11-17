// ============================================================
// Smart Tourist Safety and Emergency Response System
// Screen: Emergency Contacts Management
// ============================================================

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/app_theme.dart';
import '../providers/app_state_provider.dart';
import '../widgets/glass_container.dart';
import '../widgets/custom_text_field.dart';

class ContactsScreen extends StatelessWidget {
  final bool showAppBar;

  const ContactsScreen({super.key, this.showAppBar = true});

  void _showAddContactDialog(BuildContext context) {
    final formKey = GlobalKey<FormState>();
    final nameCtrl = TextEditingController();
    final phoneCtrl = TextEditingController();
    String relationship = 'Parent';

    final relations = [
      'Parent',
      'Spouse',
      'Sibling',
      'Friend',
      'Tour Guide',
      'Hotel / Host',
      'Embassy',
      'Other',
    ];

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          backgroundColor: AppTheme.bgSurface,
          title: const Row(
            children: [
              Icon(Icons.person_add_rounded, color: AppTheme.primary, size: 24),
              SizedBox(width: 10),
              Text('Add Emergency Contact'),
            ],
          ),
          content: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  CustomTextField(
                    controller: nameCtrl,
                    label: 'Contact Name',
                    hint: 'e.g. Sarah Smith',
                    prefixIcon: Icons.badge_outlined,
                    validator: (v) =>
                        (v == null || v.trim().isEmpty) ? 'Required' : null,
                  ),
                  const SizedBox(height: 12),
                  CustomTextField(
                    controller: phoneCtrl,
                    label: 'Phone Number',
                    hint: 'e.g. 9876543210',
                    prefixIcon: Icons.phone_outlined,
                    keyboardType: TextInputType.phone,
                    validator: (v) =>
                        (v == null || v.trim().length < 10) ? 'Valid phone required' : null,
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Relationship',
                    style: TextStyle(
                      color: AppTheme.textMuted,
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    decoration: BoxDecoration(
                      color: AppTheme.bgCard,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppTheme.borderSubtle),
                    ),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: relationship,
                        isExpanded: true,
                        dropdownColor: AppTheme.bgSurface,
                        style: const TextStyle(color: AppTheme.textMain, fontSize: 14),
                        items: relations
                            .map((r) => DropdownMenuItem(value: r, child: Text(r)))
                            .toList(),
                        onChanged: (val) {
                          if (val != null) setState(() => relationship = val);
                        },
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel', style: TextStyle(color: AppTheme.textDim)),
            ),
            ElevatedButton(
              onPressed: () async {
                if (!formKey.currentState!.validate()) return;
                Navigator.pop(ctx);
                final provider =
                    Provider.of<AppStateProvider>(context, listen: false);
                final ok = await provider.addContact(
                  name: nameCtrl.text.trim(),
                  phone: phoneCtrl.text.trim(),
                  relationship: relationship,
                );
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(ok
                          ? 'Emergency contact saved!'
                          : 'Failed to add contact: ${provider.errorMessage}'),
                      backgroundColor: ok ? AppTheme.success : AppTheme.danger,
                    ),
                  );
                }
              },
              child: const Text('Save Contact'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<AppStateProvider>(context);
    final contacts = provider.contacts;

    final body = SafeArea(
      child: RefreshIndicator(
        onRefresh: () => provider.loadContacts(),
        color: AppTheme.primaryLight,
        backgroundColor: AppTheme.bgSurface,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Emergency Contacts',
                        style: TextStyle(
                          color: AppTheme.textMain,
                          fontSize: 20,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      SizedBox(height: 2),
                      Text(
                        'Alerted immediately upon SOS beacon activation',
                        style: TextStyle(
                          color: AppTheme.textDim,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                  ElevatedButton.icon(
                    onPressed: () => _showAddContactDialog(context),
                    icon: const Icon(Icons.add, size: 16),
                    label: const Text('Add'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),

              if (contacts.isEmpty)
                GlassContainer(
                  padding: const EdgeInsets.symmetric(vertical: 40, horizontal: 20),
                  child: Center(
                    child: Column(
                      children: [
                        Icon(
                          Icons.contact_emergency_outlined,
                          size: 48,
                          color: AppTheme.textDim.withOpacity(0.5),
                        ),
                        const SizedBox(height: 12),
                        const Text(
                          'No Emergency Contacts Yet',
                          style: TextStyle(
                            color: AppTheme.textMain,
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'Add family, friends, or tour leads who should receive real-time SOS alerts.',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: AppTheme.textMuted,
                            fontSize: 12,
                          ),
                        ),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: () => _showAddContactDialog(context),
                          child: const Text('Add First Contact'),
                        ),
                      ],
                    ),
                  ),
                )
              else
                ...contacts.map((c) => GlassContainer(
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.all(16),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: AppTheme.primary.withOpacity(0.12),
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(
                              Icons.person_rounded,
                              color: AppTheme.primaryLight,
                              size: 22,
                            ),
                          ),
                          const SizedBox(width: 14),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Text(
                                      c.name,
                                      style: const TextStyle(
                                        color: AppTheme.textMain,
                                        fontSize: 15,
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 8,
                                        vertical: 2,
                                      ),
                                      decoration: BoxDecoration(
                                        color: AppTheme.cyan.withOpacity(0.12),
                                        borderRadius: BorderRadius.circular(6),
                                      ),
                                      child: Text(
                                        c.relationship,
                                        style: const TextStyle(
                                          color: AppTheme.cyan,
                                          fontSize: 10,
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 4),
                                Row(
                                  children: [
                                    const Icon(
                                      Icons.phone,
                                      color: AppTheme.textDim,
                                      size: 13,
                                    ),
                                    const SizedBox(width: 5),
                                    Text(
                                      c.phone,
                                      style: const TextStyle(
                                        color: AppTheme.textMuted,
                                        fontSize: 13,
                                        fontFamily: 'monospace',
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                          IconButton(
                            icon: const Icon(
                              Icons.delete_outline_rounded,
                              color: AppTheme.danger,
                              size: 20,
                            ),
                            onPressed: () async {
                              final confirm = await showDialog<bool>(
                                context: context,
                                builder: (ctx) => AlertDialog(
                                  backgroundColor: AppTheme.bgSurface,
                                  title: const Text('Delete Contact'),
                                  content: Text('Remove ${c.name} from emergency contacts?'),
                                  actions: [
                                    TextButton(
                                      onPressed: () => Navigator.pop(ctx, false),
                                      child: const Text('Cancel'),
                                    ),
                                    ElevatedButton(
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: AppTheme.danger,
                                      ),
                                      onPressed: () => Navigator.pop(ctx, true),
                                      child: const Text('Delete'),
                                    ),
                                  ],
                                ),
                              );

                              if (confirm == true) {
                                await provider.deleteContact(c.contactId);
                              }
                            },
                          ),
                        ],
                      ),
                    )),
            ],
          ),
        ),
      ),
    );

    if (!showAppBar) return body;

    return Scaffold(
      backgroundColor: AppTheme.bgDark,
      appBar: AppBar(
        title: const Text('EMERGENCY CONTACTS'),
        backgroundColor: AppTheme.bgSurface,
      ),
      body: body,
    );
  }
}
