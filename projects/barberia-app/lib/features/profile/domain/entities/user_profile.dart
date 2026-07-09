import '../../../../core/navigation/user_role.dart';

class UserProfile {
  const UserProfile({
    required this.id,
    required this.email,
    required this.role,
    required this.fullName,
    this.phone,
    this.bio,
    this.photoUrl,
  });

  final String id;
  final String email;
  final UserRole role;
  final String fullName;
  final String? phone;
  final String? bio;
  final String? photoUrl;
}
