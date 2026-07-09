class ServiceItem {
  const ServiceItem({
    required this.id,
    required this.name,
    required this.durationMinutes,
    required this.priceDop,
    this.description,
  });

  final String id;
  final String name;
  final int durationMinutes;
  final String priceDop;
  final String? description;
}
