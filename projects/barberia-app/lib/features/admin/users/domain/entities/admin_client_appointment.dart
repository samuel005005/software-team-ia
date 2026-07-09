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

  static const _voidableStatuses = {
    'pendiente',
    'confirmada',
    'en_progreso',
    'no_show',
  };

  bool canBeVoidedByAdmin() => _voidableStatuses.contains(status);
}
