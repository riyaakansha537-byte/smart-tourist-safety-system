// ============================================================
// Smart Tourist Safety and Emergency Response System
// Model: Tourist Profile
// ============================================================

class Tourist {
  final int touristId;
  final String name;
  final String phone;
  final String email;
  final String? nationality;
  final String? bloodGroup;
  final String? registeredAt;

  Tourist({
    required this.touristId,
    required this.name,
    required this.phone,
    required this.email,
    this.nationality,
    this.bloodGroup,
    this.registeredAt,
  });

  factory Tourist.fromJson(Map<String, dynamic> json) {
    return Tourist(
      touristId: json['tourist_id'] as int,
      name: json['name'] as String,
      phone: json['phone'] as String,
      email: json['email'] as String,
      nationality: json['nationality'] as String?,
      bloodGroup: json['blood_group'] as String?,
      registeredAt: json['registered_at'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'tourist_id': touristId,
      'name': name,
      'phone': phone,
      'email': email,
      'nationality': nationality,
      'blood_group': bloodGroup,
      'registered_at': registeredAt,
    };
  }
}
