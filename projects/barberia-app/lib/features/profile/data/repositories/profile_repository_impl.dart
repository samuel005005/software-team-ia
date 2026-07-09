import '../../../../core/utils/result.dart';
import '../../domain/entities/user_profile.dart';
import '../../domain/repositories/profile_repository.dart';
import '../datasources/profile_remote_data_source.dart';
import '../models/profile_dtos.dart';

class ProfileRepositoryImpl implements ProfileRepository {
  ProfileRepositoryImpl(this._remote);

  final ProfileRemoteDataSource _remote;

  @override
  Future<Result<UserProfile>> getMyProfile() async {
    final result = await _remote.execute(_remote.getMyProfile);
    return result.when(
      success: (dto) => Success(dto.toEntity()),
      error: (failure) => Error(failure),
    );
  }

  @override
  Future<Result<UserProfile>> updateMyProfile({
    String? fullName,
    String? phone,
    String? bio,
    String? photoUrl,
  }) async {
    final result = await _remote.execute(
      () => _remote.updateMyProfile(
        UpdateProfileRequestDto(
          fullName: fullName,
          phone: phone,
          bio: bio,
          photoUrl: photoUrl,
        ),
      ),
    );

    return result.when(
      success: (dto) => Success(dto.toEntity()),
      error: (failure) => Error(failure),
    );
  }
}
