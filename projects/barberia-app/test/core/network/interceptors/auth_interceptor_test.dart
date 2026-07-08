import 'package:barberia_app/core/network/contracts/auth_token_provider.dart';
import 'package:barberia_app/core/network/interceptors/auth_interceptor.dart';
import 'package:barberia_app/core/network/network_constants.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeTokenProvider implements AuthTokenProvider {
  _FakeTokenProvider(this._access);

  String? _access;

  @override
  String? get accessToken => _access;

  @override
  String? get refreshToken => null;

  @override
  void clear() => _access = null;

  @override
  void setTokens(tokens) {
    _access = tokens.accessToken;
  }
}

void main() {
  group('AuthInterceptor', () {
    late AuthInterceptor interceptor;

    test('agrega Authorization en rutas protegidas', () {
      interceptor = AuthInterceptor(
        tokenProvider: _FakeTokenProvider('token-abc'),
      );
      final options = RequestOptions(path: '/services');

      interceptor.onRequest(options, RequestInterceptorHandler());

      expect(
        options.headers[NetworkConstants.authorizationHeader],
        '${NetworkConstants.bearerPrefix}token-abc',
      );
    });

    test('no agrega Authorization en rutas públicas de auth', () {
      interceptor = AuthInterceptor(
        tokenProvider: _FakeTokenProvider('token-abc'),
      );
      final options = RequestOptions(path: '/auth/login');

      interceptor.onRequest(options, RequestInterceptorHandler());

      expect(options.headers[NetworkConstants.authorizationHeader], isNull);
    });

    test('no agrega Authorization si no hay token', () {
      interceptor = AuthInterceptor(
        tokenProvider: _FakeTokenProvider(null),
      );
      final options = RequestOptions(path: '/appointments');

      interceptor.onRequest(options, RequestInterceptorHandler());

      expect(options.headers[NetworkConstants.authorizationHeader], isNull);
    });
  });
}
