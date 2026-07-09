class BarberScheduleAppointment {
  const BarberScheduleAppointment({
    required this.id,
    required this.status,
    required this.scheduledStart,
    required this.scheduledEnd,
    required this.serviceId,
    required this.serviceName,
    required this.clientUserId,
    required this.clientDisplayName,
  });

  final String id;
  final String status;
  final DateTime scheduledStart;
  final DateTime scheduledEnd;
  final String serviceId;
  final String serviceName;
  final String clientUserId;
  final String clientDisplayName;
}
