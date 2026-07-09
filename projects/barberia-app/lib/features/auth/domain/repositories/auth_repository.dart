import '../../../../core/network/contracts/auth_token_provider.dart';
import '../../../../core/utils/result.dart';
import '../entities/login_result.dart';
import '../entities/register_result.dart';

abstract class AuthRepository {
  Future<Result<LoginResult>> login({
    required String email,
    required String password,
  });

  Future<Result<RegisterResult>> register({
    required String email,
    required String password,
    required String fullName,
    required String phone,
  });

  Future<Result<AuthTokens>> refresh({
    required String refreshToken,
  });
}
