import '../../domain/entities/availability_day.dart';

class AvailabilityDayDto {
  AvailabilityDayDto({
    required this.weekday,
    required this.startTime,
    required this.endTime,
    required this.isActive,
  });

  factory AvailabilityDayDto.fromJson(Map<String, dynamic> json) {
    return AvailabilityDayDto(
      weekday: json['weekday'] as int,
      startTime: json['start_time'] as String,
      endTime: json['end_time'] as String,
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  final int weekday;
  final String startTime;
  final String endTime;
  final bool isActive;

  AvailabilityDay toEntity() {
    return AvailabilityDay(
      weekday: weekday,
      startTime: startTime,
      endTime: endTime,
      isActive: isActive,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'weekday': weekday,
      'start_time': startTime,
      'end_time': endTime,
      'is_active': isActive,
    };
  }
}

class BarberAvailabilityListResponseDto {
  BarberAvailabilityListResponseDto({required this.items});

  factory BarberAvailabilityListResponseDto.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List<dynamic>? ?? const [];
    return BarberAvailabilityListResponseDto(
      items: rawItems
          .map(
            (item) => AvailabilityDayDto.fromJson(item as Map<String, dynamic>),
          )
          .toList(),
    );
  }

  final List<AvailabilityDayDto> items;
}

class UpdateBarberAvailabilityRequestDto {
  const UpdateBarberAvailabilityRequestDto({required this.items});

  final List<AvailabilityDayDto> items;

  Map<String, dynamic> toJson() {
    return {
      'items': items.map((item) => item.toJson()).toList(),
    };
  }
}
