class AppointmentSummary {
  const AppointmentSummary({
    required this.id,
    required this.status,
    required this.scheduledStart,
    required this.scheduledEnd,
    required this.serviceName,
    required this.barberDisplayName,
  });

  final String id;
  final String status;
  final DateTime scheduledStart;
  final DateTime scheduledEnd;
  final String serviceName;
  final String barberDisplayName;

  bool isUpcoming(DateTime now) =>
      !scheduledStart.isBefore(now);

  static const _cancellableStatuses = {'pendiente', 'confirmada'};
  static const cancellationNoticeHours = 2;

  bool canBeCancelledByClient(DateTime now) {
    if (!_cancellableStatuses.contains(status)) return false;
    if (scheduledStart.isBefore(now)) return false;
    return scheduledStart.difference(now) >=
        const Duration(hours: cancellationNoticeHours);
  }
}
