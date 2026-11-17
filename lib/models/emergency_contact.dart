// ============================================================
// Smart Tourist Safety and Emergency Response System
// Model: Emergency Contact
// ============================================================

class EmergencyContact {
  final int contactId;
  final int touristId;
  final String name;
  final String phone;
  final String relationship;

  EmergencyContact({
    required this.contactId,
    required this.touristId,
    required this.name,
    required this.phone,
    required this.relationship,
  });

  factory EmergencyContact.fromJson(Map<String, dynamic> json) {
    return EmergencyContact(
      contactId: json['contact_id'] as int,
      touristId: json['tourist_id'] as int,
      name: json['name'] as String,
      phone: json['phone'] as String,
      relationship: json['relationship'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'contact_id': contactId,
      'tourist_id': touristId,
      'name': name,
      'phone': phone,
      'relationship': relationship,
    };
  }
}
