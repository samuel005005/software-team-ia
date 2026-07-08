import 'package:dio/dio.dart';

import '../network_constants.dart';

typedef RefreshTokenCallback = Future<bool> Function();
typedef SessionExpiredCallback = void Function();

/// Maneja respuestas 401 en rutas protegidas.
///
/// El refresh real de tokens se implementará en T-031.
class UnauthorizedInterceptor extends Interceptor {
  UnauthorizedInterceptor({
    required RefreshTokenCallback onRefreshToken,
    required SessionExpiredCallback onSessionExpired,
  })  : _onRefreshToken = onRefreshToken,
        _onSessionExpired = onSessionExpired;

  final RefreshTokenCallback _onRefreshToken;
  final SessionExpiredCallback _onSessionExpired;

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    final statusCode = err.response?.statusCode;
    final path = err.requestOptions.path;

    if (statusCode == 401 && !NetworkConstants.isPublicAuthPath(path)) {
      final refreshed = await _onRefreshToken();
      if (!refreshed) {
        _onSessionExpired();
      }
    }

    handler.next(err);
  }
}
