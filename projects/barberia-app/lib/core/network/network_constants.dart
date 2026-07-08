/// Constantes de red compartidas.
abstract final class NetworkConstants {
  static const String authorizationHeader = 'Authorization';
  static const String bearerPrefix = 'Bearer ';

  /// Rutas públicas que no requieren token JWT.
  static const publicAuthPaths = {
    '/auth/login',
    '/auth/register',
    '/auth/refresh',
  };

  static bool isPublicAuthPath(String path) {
    return publicAuthPaths.any(
      (publicPath) => path.endsWith(publicPath) || path.contains(publicPath),
    );
  }
}
