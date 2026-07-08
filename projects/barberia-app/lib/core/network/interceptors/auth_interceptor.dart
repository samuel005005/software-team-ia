import 'package:dio/dio.dart';

import '../contracts/auth_token_provider.dart';
import '../network_constants.dart';

/// Agrega el header `Authorization` a peticiones protegidas.
class AuthInterceptor extends Interceptor {
  AuthInterceptor({required AuthTokenProvider tokenProvider})
      : _tokenProvider = tokenProvider;

  final AuthTokenProvider _tokenProvider;

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    if (!NetworkConstants.isPublicAuthPath(options.path)) {
      final token = _tokenProvider.accessToken;
      if (token != null && token.isNotEmpty) {
        options.headers[NetworkConstants.authorizationHeader] =
            '${NetworkConstants.bearerPrefix}$token';
      }
    }

    handler.next(options);
  }
}
