import '../../../../core/navigation/user_role.dart';
import '../../domain/entities/user_profile.dart';

class UserProfileDto {
  UserProfileDto({
    required this.id,
    required this.email,
    required this.role,
    required this.fullName,
    this.phone,
    this.bio,
    this.photoUrl,
  });

  factory UserProfileDto.fromJson(Map<String, dynamic> json) {
    return UserProfileDto(
      id: json['id'] as String,
      email: json['email'] as String,
      role: json['role'] as String,
      fullName: json['full_name'] as String,
      phone: json['phone'] as String?,
      bio: json['bio'] as String?,
      photoUrl: json['photo_url'] as String?,
    );
  }

  final String id;
  final String email;
  final String role;
  final String fullName;
  final String? phone;
  final String? bio;
  final String? photoUrl;

  UserProfile toEntity() {
    final parsedRole = switch (role) {
      'client' => UserRole.client,
      'barber' => UserRole.barber,
      'admin' => UserRole.admin,
      _ => UserRole.client,
    };

    return UserProfile(
      id: id,
      email: email,
      role: parsedRole,
      fullName: fullName,
      phone: phone,
      bio: bio,
      photoUrl: photoUrl,
    );
  }
}

class UpdateProfileRequestDto {
  const UpdateProfileRequestDto({
    this.fullName,
    this.phone,
    this.bio,
    this.photoUrl,
  });

  final String? fullName;
  final String? phone;
  final String? bio;
  final String? photoUrl;

  Map<String, dynamic> toJson() {
    final data = <String, dynamic>{};
    if (fullName != null) data['full_name'] = fullName;
    if (phone != null) data['phone'] = phone;
    if (bio != null) data['bio'] = bio;
    if (photoUrl != null) data['photo_url'] = photoUrl;
    return data;
  }
}
