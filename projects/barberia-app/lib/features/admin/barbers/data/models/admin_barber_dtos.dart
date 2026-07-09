import '../../domain/entities/admin_barber.dart';

class AdminBarberDto {
  AdminBarberDto({
    required this.userId,
    required this.email,
    required this.displayName,
    required this.isBookable,
    required this.isActive,
    this.bio,
    this.photoUrl,
  });

  factory AdminBarberDto.fromJson(Map<String, dynamic> json) {
    return AdminBarberDto(
      userId: json['user_id'] as String,
      email: json['email'] as String,
      displayName: json['display_name'] as String,
      isBookable: json['is_bookable'] as bool? ?? true,
      isActive: json['is_active'] as bool? ?? true,
      bio: json['bio'] as String?,
      photoUrl: json['photo_url'] as String?,
    );
  }

  final String userId;
  final String email;
  final String displayName;
  final bool isBookable;
  final bool isActive;
  final String? bio;
  final String? photoUrl;

  AdminBarber toEntity() {
    return AdminBarber(
      userId: userId,
      email: email,
      displayName: displayName,
      isBookable: isBookable,
      isActive: isActive,
      bio: bio,
      photoUrl: photoUrl,
    );
  }
}

class AdminBarberListResponseDto {
  AdminBarberListResponseDto({required this.items});

  factory AdminBarberListResponseDto.fromJson(Map<String, dynamic> json) {
    final rawItems = json['items'] as List<dynamic>? ?? const [];
    return AdminBarberListResponseDto(
      items: rawItems
          .map((item) => AdminBarberDto.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  final List<AdminBarberDto> items;
}

class CreateAdminBarberRequestDto {
  const CreateAdminBarberRequestDto({
    required this.email,
    required this.password,
    required this.displayName,
    this.bio,
    this.photoUrl,
    this.isBookable = true,
  });

  final String email;
  final String password;
  final String displayName;
  final String? bio;
  final String? photoUrl;
  final bool isBookable;

  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
      'display_name': displayName,
      if (bio != null && bio!.isNotEmpty) 'bio': bio,
      if (photoUrl != null && photoUrl!.isNotEmpty) 'photo_url': photoUrl,
      'is_bookable': isBookable,
    };
  }
}

class UpdateAdminBarberRequestDto {
  const UpdateAdminBarberRequestDto({
    this.displayName,
    this.bio,
    this.photoUrl,
    this.isBookable,
    this.isActive,
  });

  final String? displayName;
  final String? bio;
  final String? photoUrl;
  final bool? isBookable;
  final bool? isActive;

  Map<String, dynamic> toJson() {
    final data = <String, dynamic>{};
    if (displayName != null) data['display_name'] = displayName;
    if (bio != null) data['bio'] = bio;
    if (photoUrl != null) data['photo_url'] = photoUrl;
    if (isBookable != null) data['is_bookable'] = isBookable;
    if (isActive != null) data['is_active'] = isActive;
    return data;
  }
}
