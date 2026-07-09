import '../../../../core/navigation/user_role.dart';
import '../../../../core/network/contracts/auth_token_provider.dart';

/// Resultado de login exitoso (US-002).
class LoginResult {
  const LoginResult({
    required this.tokens,
    required this.role,
  });

  final AuthTokens tokens;
  final UserRole role;
}
