class AdminClientAppointment {
  const AdminClientAppointment({
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
}
