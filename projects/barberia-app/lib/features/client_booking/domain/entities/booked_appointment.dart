class BookedAppointment {
  const BookedAppointment({
    required this.id,
    required this.status,
    required this.scheduledStart,
    required this.scheduledEnd,
    required this.serviceId,
    required this.serviceName,
    required this.barberUserId,
    required this.barberDisplayName,
  });

  final String id;
  final String status;
  final DateTime scheduledStart;
  final DateTime scheduledEnd;
  final String serviceId;
  final String serviceName;
  final String barberUserId;
  final String barberDisplayName;
}
