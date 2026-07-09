class AdminService {
  const AdminService({
    required this.id,
    required this.name,
    required this.durationMinutes,
    required this.priceDop,
    required this.isActive,
    this.description,
  });

  final String id;
  final String name;
  final int durationMinutes;
  final String priceDop;
  final bool isActive;
  final String? description;
}
