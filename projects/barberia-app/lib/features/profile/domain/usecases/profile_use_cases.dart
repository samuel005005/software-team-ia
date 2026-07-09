import '../../../../core/application/use_case.dart';
import '../../../../core/utils/result.dart';
import '../entities/user_profile.dart';
import '../repositories/profile_repository.dart';

class GetMyProfileUseCase extends UseCase<UserProfile, NoParams> {
  GetMyProfileUseCase(this._repository);

  final ProfileRepository _repository;

  @override
  Future<Result<UserProfile>> call(NoParams params) {
    return _repository.getMyProfile();
  }
}

class UpdateMyProfileParams {
  const UpdateMyProfileParams({
    this.fullName,
    this.phone,
    this.bio,
    this.photoUrl,
  });

  final String? fullName;
  final String? phone;
  final String? bio;
  final String? photoUrl;
}

class UpdateMyProfileUseCase extends UseCase<UserProfile, UpdateMyProfileParams> {
  UpdateMyProfileUseCase(this._repository);

  final ProfileRepository _repository;

  @override
  Future<Result<UserProfile>> call(UpdateMyProfileParams params) {
    return _repository.updateMyProfile(
      fullName: params.fullName,
      phone: params.phone,
      bio: params.bio,
      photoUrl: params.photoUrl,
    );
  }
}
