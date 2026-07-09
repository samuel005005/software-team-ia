import '../../domain/entities/admin_client.dart';
import '../../domain/entities/admin_client_appointment.dart';

class AdminClientDto {
  AdminClientDto({
    required this.userId,
    required this.email,
    required this.fullName,
    required this.phone,
    required this.isActive,
  });

  factory AdminClientDto.fromJson(Map<String, dynamic> json) {
    return AdminClientDto(
      userId: json['user_id'] as String,
      email: json['email'] as String,
      fullName: json['full_name'] as String,
      phone: json['phone'] as String,
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  final String userId;
  final String email;
  final String fullName;
  final String phone;
  final bool isActive;

  AdminClient toEntity() {
    return AdminClient(
      userId: userId,
      email: email,
      fullName: fullName,
      phone: phone,
      isActive: isActive,
    );
  }
}

class AdminClientListResponseDto {
  AdminClientListResponseDto({required this.items});

  factory AdminClientListResponseDto.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List<dynamic>? ?? const [];
    return AdminClientListResponseDto(
      items: rawItems
          .map((item) => AdminClientDto.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  final List<AdminClientDto> items;
}

class UpdateAdminClientRequestDto {
  const UpdateAdminClientRequestDto({this.isActive});

  final bool? isActive;

  Map<String, dynamic> toJson() {
    final data = <String, dynamic>{};
    if (isActive != null) data['is_active'] = isActive;
    return data;
  }
}

class AdminClientAppointmentDto {
  AdminClientAppointmentDto({
    required this.id,
    required this.status,
    required this.scheduledStart,
    required this.scheduledEnd,
    required this.serviceName,
    required this.barberDisplayName,
  });

  factory AdminClientAppointmentDto.fromJson(Map<String, dynamic> json) {
    return AdminClientAppointmentDto(
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

  AdminClientAppointment toEntity() {
    return AdminClientAppointment(
      id: id,
      status: status,
      scheduledStart: scheduledStart,
      scheduledEnd: scheduledEnd,
      serviceName: serviceName,
      barberDisplayName: barberDisplayName,
    );
  }
}

class AdminClientAppointmentListResponseDto {
  AdminClientAppointmentListResponseDto({required this.items});

  factory AdminClientAppointmentListResponseDto.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List<dynamic>? ?? const [];
    return AdminClientAppointmentListResponseDto(
      items: rawItems
          .map(
            (item) => AdminClientAppointmentDto.fromJson(item as Map<String, dynamic>),
          )
          .toList(),
    );
  }

  final List<AdminClientAppointmentDto> items;
}
