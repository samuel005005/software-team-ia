import '../../domain/entities/business_hours_day.dart';

class BusinessHoursDayDto {
  BusinessHoursDayDto({
    required this.weekday,
    required this.openTime,
    required this.closeTime,
    required this.isClosed,
  });

  factory BusinessHoursDayDto.fromJson(Map<String, dynamic> json) {
    return BusinessHoursDayDto(
      weekday: json['weekday'] as int,
      openTime: json['open_time'] as String,
      closeTime: json['close_time'] as String,
      isClosed: json['is_closed'] as bool? ?? false,
    );
  }

  final int weekday;
  final String openTime;
  final String closeTime;
  final bool isClosed;

  BusinessHoursDay toEntity() {
    return BusinessHoursDay(
      weekday: weekday,
      openTime: openTime,
      closeTime: closeTime,
      isClosed: isClosed,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'weekday': weekday,
      'open_time': openTime,
      'close_time': closeTime,
      'is_closed': isClosed,
    };
  }
}

class BusinessHoursListResponseDto {
  BusinessHoursListResponseDto({required this.items});

  factory BusinessHoursListResponseDto.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List<dynamic>? ?? const [];
    return BusinessHoursListResponseDto(
      items: rawItems
          .map(
            (item) => BusinessHoursDayDto.fromJson(item as Map<String, dynamic>),
          )
          .toList(),
    );
  }

  final List<BusinessHoursDayDto> items;
}

class UpdateBusinessHoursRequestDto {
  const UpdateBusinessHoursRequestDto({required this.items});

  final List<BusinessHoursDayDto> items;

  Map<String, dynamic> toJson() {
    return {
      'items': items.map((item) => item.toJson()).toList(),
    };
  }
}
