class AdminBarber {
  const AdminBarber({
    required this.userId,
    required this.email,
    required this.displayName,
    required this.isBookable,
    required this.isActive,
    this.bio,
    this.photoUrl,
  });

  final String userId;
  final String email;
  final String displayName;
  final bool isBookable;
  final bool isActive;
  final String? bio;
  final String? photoUrl;
}
