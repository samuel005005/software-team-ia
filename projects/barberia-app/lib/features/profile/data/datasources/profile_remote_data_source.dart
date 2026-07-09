import '../../../../core/network/remote_data_source.dart';
import '../models/profile_dtos.dart';

class ProfileRemoteDataSource extends RemoteDataSource {
  ProfileRemoteDataSource(super.dio);

  Future<UserProfileDto> getMyProfile() async {
    final response = await dio.get<Map<String, dynamic>>('/me');
    return UserProfileDto.fromJson(response.data!);
  }

  Future<UserProfileDto> updateMyProfile(UpdateProfileRequestDto request) async {
    final response = await dio.patch<Map<String, dynamic>>(
      '/me',
      data: request.toJson(),
    );
    return UserProfileDto.fromJson(response.data!);
  }
}
