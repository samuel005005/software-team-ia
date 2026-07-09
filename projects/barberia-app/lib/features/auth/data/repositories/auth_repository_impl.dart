import '../../../../core/error/failures.dart';
import '../../../../core/network/contracts/auth_token_provider.dart';
import '../../../../core/utils/jwt_decoder.dart';
import '../../../../core/utils/result.dart';
import '../../domain/entities/login_result.dart';
import '../../domain/entities/register_result.dart';
import '../../domain/repositories/auth_repository.dart';
import '../datasources/auth_remote_data_source.dart';
import '../models/auth_dtos.dart';

class AuthRepositoryImpl implements AuthRepository {
  AuthRepositoryImpl(this._remote);

  final AuthRemoteDataSource _remote;

  @override
  Future<Result<LoginResult>> login({
    required String email,
    required String password,
  }) async {
    final result = await _remote.execute(
      () => _remote.login(
        LoginRequestDto(email: email.trim(), password: password),
      ),
    );

    return result.when(
      success: (dto) {
        final tokens = dto.toTokens();
        final role = JwtDecoder.extractRole(tokens.accessToken);
        if (role == null) {
          return const Error(UnknownFailure('No se pudo leer el rol del token.'));
        }
        return Success(LoginResult(tokens: tokens, role: role));
      },
      error: (failure) => Error(failure),
    );
  }

  @override
  Future<Result<RegisterResult>> register({
    required String email,
    required String password,
    required String fullName,
    required String phone,
  }) async {
    final result = await _remote.execute(
      () => _remote.register(
        RegisterRequestDto(
          email: email.trim(),
          password: password,
          fullName: fullName.trim(),
          phone: phone.trim(),
        ),
      ),
    );

    return result.when(
      success: (dto) => Success(dto.toEntity()),
      error: (failure) => Error(failure),
    );
  }

  @override
  Future<Result<AuthTokens>> refresh({required String refreshToken}) async {
    final result = await _remote.execute(
      () => _remote.refresh(RefreshRequestDto(refreshToken: refreshToken)),
    );

    return result.when(
      success: (dto) => Success(dto.toTokens()),
      error: (failure) => Error(failure),
    );
  }
}
