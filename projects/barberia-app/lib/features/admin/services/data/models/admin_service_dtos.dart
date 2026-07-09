import '../../domain/entities/admin_service.dart';

class AdminServiceDto {
  AdminServiceDto({
    required this.id,
    required this.name,
    required this.durationMinutes,
    required this.priceDop,
    required this.isActive,
    this.description,
  });

  factory AdminServiceDto.fromJson(Map<String, dynamic> json) {
    return AdminServiceDto(
      id: json['id'] as String,
      name: json['name'] as String,
      durationMinutes: json['duration_minutes'] as int,
      priceDop: json['price_dop'] as String,
      isActive: json['is_active'] as bool? ?? true,
      description: json['description'] as String?,
    );
  }

  final String id;
  final String name;
  final int durationMinutes;
  final String priceDop;
  final bool isActive;
  final String? description;

  AdminService toEntity() {
    return AdminService(
      id: id,
      name: name,
      durationMinutes: durationMinutes,
      priceDop: priceDop,
      isActive: isActive,
      description: description,
    );
  }
}

class AdminServiceListResponseDto {
  AdminServiceListResponseDto({required this.items});

  factory AdminServiceListResponseDto.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List<dynamic>? ?? const [];
    return AdminServiceListResponseDto(
      items: rawItems
          .map((item) => AdminServiceDto.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  final List<AdminServiceDto> items;
}

class CreateAdminServiceRequestDto {
  const CreateAdminServiceRequestDto({
    required this.name,
    required this.durationMinutes,
    required this.priceDop,
    this.description,
    this.isActive = true,
  });

  final String name;
  final int durationMinutes;
  final String priceDop;
  final String? description;
  final bool isActive;

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'duration_minutes': durationMinutes,
      'price_dop': priceDop,
      if (description != null && description!.isNotEmpty) 'description': description,
      'is_active': isActive,
    };
  }
}

class UpdateAdminServiceRequestDto {
  const UpdateAdminServiceRequestDto({
    this.name,
    this.durationMinutes,
    this.priceDop,
    this.description,
    this.isActive,
  });

  final String? name;
  final int? durationMinutes;
  final String? priceDop;
  final String? description;
  final bool? isActive;

  Map<String, dynamic> toJson() {
    final data = <String, dynamic>{};
    if (name != null) data['name'] = name;
    if (durationMinutes != null) data['duration_minutes'] = durationMinutes;
    if (priceDop != null) data['price_dop'] = priceDop;
    if (description != null) data['description'] = description;
    if (isActive != null) data['is_active'] = isActive;
    return data;
  }
}
