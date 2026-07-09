class AdminClient {
  const AdminClient({
    required this.userId,
    required this.email,
    required this.fullName,
    required this.phone,
    required this.isActive,
  });

  final String userId;
  final String email;
  final String fullName;
  final String phone;
  final bool isActive;
}
