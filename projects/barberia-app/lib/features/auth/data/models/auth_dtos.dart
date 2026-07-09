import '../../domain/entities/register_result.dart';
import '../../../../core/network/contracts/auth_token_provider.dart';

class LoginRequestDto {
  const LoginRequestDto({required this.email, required this.password});

  final String email;
  final String password;

  Map<String, dynamic> toJson() => {
        'email': email,
        'password': password,
      };
}

class RegisterRequestDto {
  const RegisterRequestDto({
    required this.email,
    required this.password,
    required this.fullName,
    required this.phone,
  });

  final String email;
  final String password;
  final String fullName;
  final String phone;

  Map<String, dynamic> toJson() => {
        'email': email,
        'password': password,
        'full_name': fullName,
        'phone': phone,
      };
}

class TokenResponseDto {
  TokenResponseDto({
    required this.accessToken,
    required this.refreshToken,
    this.tokenType = 'bearer',
  });

  factory TokenResponseDto.fromJson(Map<String, dynamic> json) {
    return TokenResponseDto(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
      tokenType: json['token_type'] as String? ?? 'bearer',
    );
  }

  final String accessToken;
  final String refreshToken;
  final String tokenType;

  AuthTokens toTokens() => AuthTokens(
        accessToken: accessToken,
        refreshToken: refreshToken,
      );
}

class RegisterResponseDto {
  RegisterResponseDto({
    required this.id,
    required this.email,
    required this.fullName,
    required this.message,
  });

  factory RegisterResponseDto.fromJson(Map<String, dynamic> json) {
    return RegisterResponseDto(
      id: json['id'] as String,
      email: json['email'] as String,
      fullName: json['full_name'] as String,
      message: json['message'] as String? ?? 'Registro exitoso',
    );
  }

  final String id;
  final String email;
  final String fullName;
  final String message;

  RegisterResult toEntity() => RegisterResult(
        id: id,
        email: email,
        fullName: fullName,
        message: message,
      );
}

class RefreshRequestDto {
  const RefreshRequestDto({required this.refreshToken});

  final String refreshToken;

  Map<String, dynamic> toJson() => {'refresh_token': refreshToken};
}
