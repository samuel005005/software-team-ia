import '../../../../core/application/use_case.dart';
import '../../../../core/utils/result.dart';
import '../entities/register_result.dart';
import '../repositories/auth_repository.dart';

class RegisterParams {
  const RegisterParams({
    required this.email,
    required this.password,
    required this.fullName,
    required this.phone,
  });

  final String email;
  final String password;
  final String fullName;
  final String phone;
}

class RegisterUseCase extends UseCase<RegisterResult, RegisterParams> {
  RegisterUseCase(this._repository);

  final AuthRepository _repository;

  @override
  Future<Result<RegisterResult>> call(RegisterParams params) {
    return _repository.register(
      email: params.email,
      password: params.password,
      fullName: params.fullName,
      phone: params.phone,
    );
  }
}
