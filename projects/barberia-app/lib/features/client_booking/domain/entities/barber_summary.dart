class BarberSummary {
  const BarberSummary({
    required this.userId,
    required this.displayName,
    this.bio,
    this.photoUrl,
    this.isBookable = true,
  });

  final String userId;
  final String displayName;
  final String? bio;
  final String? photoUrl;
  final bool isBookable;
}
