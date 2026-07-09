import '../../domain/entities/availability_data.dart';
import '../../domain/entities/availability_slot.dart';
import '../../domain/entities/barber_summary.dart';
import '../../domain/entities/booked_appointment.dart';

class BarberSummaryDto {
  BarberSummaryDto({
    required this.userId,
    required this.displayName,
    this.bio,
    this.photoUrl,
    this.isBookable = true,
  });

  factory BarberSummaryDto.fromJson(Map<String, dynamic> json) {
    return BarberSummaryDto(
      userId: json['user_id'] as String,
      displayName: json['display_name'] as String,
      bio: json['bio'] as String?,
      photoUrl: json['photo_url'] as String?,
      isBookable: json['is_bookable'] as bool? ?? true,
    );
  }

  final String userId;
  final String displayName;
  final String? bio;
  final String? photoUrl;
  final bool isBookable;

  BarberSummary toEntity() {
    return BarberSummary(
      userId: userId,
      displayName: displayName,
      bio: bio,
      photoUrl: photoUrl,
      isBookable: isBookable,
    );
  }
}

class BarberListResponseDto {
  BarberListResponseDto({required this.items});

  factory BarberListResponseDto.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List<dynamic>? ?? const [];
    return BarberListResponseDto(
      items: rawItems
          .map((item) => BarberSummaryDto.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  final List<BarberSummaryDto> items;
}

class AvailabilitySlotDto {
  AvailabilitySlotDto({
    required this.start,
    required this.end,
    required this.barberUserId,
    required this.startIso,
  });

  factory AvailabilitySlotDto.fromJson(Map<String, dynamic> json) {
    final startRaw = json['start'] as String;
    return AvailabilitySlotDto(
      start: DateTime.parse(startRaw),
      end: DateTime.parse(json['end'] as String),
      barberUserId: json['barber_user_id'] as String,
      startIso: startRaw,
    );
  }

  final DateTime start;
  final DateTime end;
  final String barberUserId;
  final String startIso;

  AvailabilitySlot toEntity() {
    return AvailabilitySlot(
      start: start,
      end: end,
      barberUserId: barberUserId,
      startIso: startIso,
    );
  }
}

class AvailabilityResponseDto {
  AvailabilityResponseDto({
    required this.serviceId,
    required this.date,
    required this.barbers,
    required this.slots,
  });

  factory AvailabilityResponseDto.fromJson(Map<String, dynamic> json) {
    final rawBarbers = json['barbers'] as List<dynamic>? ?? const [];
    final rawSlots = json['slots'] as List<dynamic>? ?? const [];

    return AvailabilityResponseDto(
      serviceId: json['service_id'] as String,
      date: DateTime.parse(json['date'] as String),
      barbers: rawBarbers
          .map((item) => BarberSummaryDto.fromJson(item as Map<String, dynamic>))
          .toList(),
      slots: rawSlots
          .map((item) => AvailabilitySlotDto.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  final String serviceId;
  final DateTime date;
  final List<BarberSummaryDto> barbers;
  final List<AvailabilitySlotDto> slots;

  AvailabilityData toEntity() {
    return AvailabilityData(
      serviceId: serviceId,
      date: date,
      barbers: barbers.map((barber) => barber.toEntity()).toList(),
      slots: slots.map((slot) => slot.toEntity()).toList(),
    );
  }
}

class AppointmentCreateRequestDto {
  AppointmentCreateRequestDto({
    required this.barberUserId,
    required this.serviceId,
    required this.scheduledStartIso,
  });

  final String barberUserId;
  final String serviceId;
  final String scheduledStartIso;

  Map<String, dynamic> toJson() {
    return {
      'barber_user_id': barberUserId,
      'service_id': serviceId,
      'scheduled_start': scheduledStartIso,
    };
  }
}

class AppointmentResponseDto {
  AppointmentResponseDto({
    required this.id,
    required this.status,
    required this.scheduledStart,
    required this.scheduledEnd,
    required this.serviceId,
    required this.serviceName,
    required this.barberUserId,
    required this.barberDisplayName,
  });

  factory AppointmentResponseDto.fromJson(Map<String, dynamic> json) {
    return AppointmentResponseDto(
      id: json['id'] as String,
      status: json['status'] as String,
      scheduledStart: DateTime.parse(json['scheduled_start'] as String),
      scheduledEnd: DateTime.parse(json['scheduled_end'] as String),
      serviceId: json['service_id'] as String,
      serviceName: json['service_name'] as String,
      barberUserId: json['barber_user_id'] as String,
      barberDisplayName: json['barber_display_name'] as String,
    );
  }

  final String id;
  final String status;
  final DateTime scheduledStart;
  final DateTime scheduledEnd;
  final String serviceId;
  final String serviceName;
  final String barberUserId;
  final String barberDisplayName;

  BookedAppointment toEntity() {
    return BookedAppointment(
      id: id,
      status: status,
      scheduledStart: scheduledStart,
      scheduledEnd: scheduledEnd,
      serviceId: serviceId,
      serviceName: serviceName,
      barberUserId: barberUserId,
      barberDisplayName: barberDisplayName,
    );
  }
}
