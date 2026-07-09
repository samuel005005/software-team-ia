import '../../domain/entities/appointment_summary.dart';

class AppointmentSummaryDto {
  AppointmentSummaryDto({
    required this.id,
    required this.status,
    required this.scheduledStart,
    required this.scheduledEnd,
    required this.serviceName,
    required this.barberDisplayName,
  });

  factory AppointmentSummaryDto.fromJson(Map<String, dynamic> json) {
    return AppointmentSummaryDto(
      id: json['id'] as String,
      status: json['status'] as String,
      scheduledStart: DateTime.parse(json['scheduled_start'] as String),
      scheduledEnd: DateTime.parse(json['scheduled_end'] as String),
      serviceName: json['service_name'] as String,
      barberDisplayName: json['barber_display_name'] as String,
    );
  }

  final String id;
  final String status;
  final DateTime scheduledStart;
  final DateTime scheduledEnd;
  final String serviceName;
  final String barberDisplayName;

  AppointmentSummary toEntity() {
    return AppointmentSummary(
      id: id,
      status: status,
      scheduledStart: scheduledStart,
      scheduledEnd: scheduledEnd,
      serviceName: serviceName,
      barberDisplayName: barberDisplayName,
    );
  }
}

class AppointmentListResponseDto {
  AppointmentListResponseDto({required this.items});

  factory AppointmentListResponseDto.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List<dynamic>? ?? const [];
    return AppointmentListResponseDto(
      items: rawItems
          .map(
            (item) =>
                AppointmentSummaryDto.fromJson(item as Map<String, dynamic>),
          )
          .toList(),
    );
  }

  final List<AppointmentSummaryDto> items;
}
