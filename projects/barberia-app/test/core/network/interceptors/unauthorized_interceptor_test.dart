import 'package:barberia_app/core/network/interceptors/unauthorized_interceptor.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';

class _TestErrorHandler extends ErrorInterceptorHandler {
  DioException? forwarded;

  @override
  void next(DioException err) {
    forwarded = err;
  }
}

void main() {
  group('UnauthorizedInterceptor', () {
    test('ejecuta onSessionExpired en 401 de ruta protegida', () async {
      var expiredCalled = false;
      final interceptor = UnauthorizedInterceptor(
        onRefreshToken: () async => false,
        onSessionExpired: () => expiredCalled = true,
      );

      final error = DioException(
        requestOptions: RequestOptions(path: '/appointments'),
        type: DioExceptionType.badResponse,
        response: Response(
          requestOptions: RequestOptions(path: '/appointments'),
          statusCode: 401,
        ),
      );

      final handler = _TestErrorHandler();

      await interceptor.onError(error, handler);

      expect(expiredCalled, isTrue);
      expect(handler.forwarded, isNotNull);
    });

    test('no ejecuta onSessionExpired en rutas públicas', () async {
      var expiredCalled = false;
      final interceptor = UnauthorizedInterceptor(
        onRefreshToken: () async => false,
        onSessionExpired: () => expiredCalled = true,
      );

      final error = DioException(
        requestOptions: RequestOptions(path: '/auth/login'),
        type: DioExceptionType.badResponse,
        response: Response(
          requestOptions: RequestOptions(path: '/auth/login'),
          statusCode: 401,
        ),
      );

      final handler = _TestErrorHandler();

      await interceptor.onError(error, handler);

      expect(expiredCalled, isFalse);
      expect(handler.forwarded, isNotNull);
    });
  });
}
