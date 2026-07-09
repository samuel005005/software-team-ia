import '../../../../core/network/remote_data_source.dart';
import '../models/auth_dtos.dart';

class AuthRemoteDataSource extends RemoteDataSource {
  AuthRemoteDataSource(super.dio);

  Future<TokenResponseDto> login(LoginRequestDto request) async {
    final response = await dio.post<Map<String, dynamic>>(
      '/auth/login',
      data: request.toJson(),
    );
    return TokenResponseDto.fromJson(response.data!);
  }

  Future<RegisterResponseDto> register(RegisterRequestDto request) async {
    final response = await dio.post<Map<String, dynamic>>(
      '/auth/register',
      data: request.toJson(),
    );
    return RegisterResponseDto.fromJson(response.data!);
  }

  Future<TokenResponseDto> refresh(RefreshRequestDto request) async {
    final response = await dio.post<Map<String, dynamic>>(
      '/auth/refresh',
      data: request.toJson(),
    );
    return TokenResponseDto.fromJson(response.data!);
  }
}
