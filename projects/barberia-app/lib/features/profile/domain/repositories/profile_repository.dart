import '../../../../core/utils/result.dart';
import '../entities/user_profile.dart';

abstract class ProfileRepository {
  Future<Result<UserProfile>> getMyProfile();

  Future<Result<UserProfile>> updateMyProfile({
    String? fullName,
    String? phone,
    String? bio,
    String? photoUrl,
  });
}
