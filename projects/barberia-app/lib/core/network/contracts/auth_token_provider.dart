/// Tokens JWT de sesión.
class AuthTokens {
  const AuthTokens({
    required this.accessToken,
    required this.refreshToken,
  });

  final String accessToken;
  final String refreshToken;
}

/// Contrato para proveer tokens a la capa HTTP.
///
/// La persistencia segura se implementará en T-005.
abstract class AuthTokenProvider {
  String? get accessToken;
  String? get refreshToken;

  void setTokens(AuthTokens tokens);
  void clear();
}
