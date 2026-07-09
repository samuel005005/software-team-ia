class AvailabilitySlot {
  const AvailabilitySlot({
    required this.start,
    required this.end,
    required this.barberUserId,
    required this.startIso,
  });

  final DateTime start;
  final DateTime end;
  final String barberUserId;
  final String startIso;
}
