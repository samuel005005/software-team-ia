import '../../domain/entities/service_item.dart';

class ServiceSummaryDto {
  ServiceSummaryDto({
    required this.id,
    required this.name,
    required this.durationMinutes,
    required this.priceDop,
    this.description,
  });

  factory ServiceSummaryDto.fromJson(Map<String, dynamic> json) {
    return ServiceSummaryDto(
      id: json['id'] as String,
      name: json['name'] as String,
      durationMinutes: json['duration_minutes'] as int,
      priceDop: json['price_dop'] as String,
      description: json['description'] as String?,
    );
  }

  final String id;
  final String name;
  final int durationMinutes;
  final String priceDop;
  final String? description;

  ServiceItem toEntity() {
    return ServiceItem(
      id: id,
      name: name,
      durationMinutes: durationMinutes,
      priceDop: priceDop,
      description: description,
    );
  }
}

class ServiceListResponseDto {
  ServiceListResponseDto({required this.items});

  factory ServiceListResponseDto.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List<dynamic>? ?? const [];
    return ServiceListResponseDto(
      items: rawItems
          .map((item) => ServiceSummaryDto.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  final List<ServiceSummaryDto> items;
}
