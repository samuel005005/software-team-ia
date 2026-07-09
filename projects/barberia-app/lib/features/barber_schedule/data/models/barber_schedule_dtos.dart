import '../../domain/entities/barber_schedule_appointment.dart';

class BarberScheduleAppointmentDto {
  BarberScheduleAppointmentDto({
    required this.id,
    required this.status,
    required this.scheduledStart,
    required this.scheduledEnd,
    required this.serviceId,
    required this.serviceName,
    required this.clientUserId,
    required this.clientDisplayName,
  });

  factory BarberScheduleAppointmentDto.fromJson(Map<String, dynamic> json) {
    return BarberScheduleAppointmentDto(
      id: json['id'] as String,
      status: json['status'] as String,
      scheduledStart: DateTime.parse(json['scheduled_start'] as String),
      scheduledEnd: DateTime.parse(json['scheduled_end'] as String),
      serviceId: json['service_id'] as String,
      serviceName: json['service_name'] as String,
      clientUserId: json['client_user_id'] as String,
      clientDisplayName: json['client_display_name'] as String,
    );
  }

  final String id;
  final String status;
  final DateTime scheduledStart;
  final DateTime scheduledEnd;
  final String serviceId;
  final String serviceName;
  final String clientUserId;
  final String clientDisplayName;

  BarberScheduleAppointment toEntity() {
    return BarberScheduleAppointment(
      id: id,
      status: status,
      scheduledStart: scheduledStart,
      scheduledEnd: scheduledEnd,
      serviceId: serviceId,
      serviceName: serviceName,
      clientUserId: clientUserId,
      clientDisplayName: clientDisplayName,
    );
  }
}

class BarberScheduleResponseDto {
  BarberScheduleResponseDto({
    required this.fromDate,
    required this.toDate,
    required this.items,
  });

  factory BarberScheduleResponseDto.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List<dynamic>? ?? const [];
    return BarberScheduleResponseDto(
      fromDate: DateTime.parse(json['from_date'] as String),
      toDate: DateTime.parse(json['to_date'] as String),
      items: rawItems
          .map(
            (item) => BarberScheduleAppointmentDto.fromJson(
              item as Map<String, dynamic>,
            ),
          )
          .toList(),
    );
  }

  final DateTime fromDate;
  final DateTime toDate;
  final List<BarberScheduleAppointmentDto> items;
}
