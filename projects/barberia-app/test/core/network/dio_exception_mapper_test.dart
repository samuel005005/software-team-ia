import 'package:barberia_app/core/error/app_exception.dart';
import 'package:barberia_app/core/network/dio_exception_mapper.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('DioExceptionMapper', () {
    test('mapea timeout a NetworkException', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/test'),
        type: DioExceptionType.connectionTimeout,
      );

      final mapped = DioExceptionMapper.map(error);

      expect(mapped, isA<NetworkException>());
    });

    test('mapea 401 a UnauthorizedException', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/test'),
        type: DioExceptionType.badResponse,
        response: Response(
          requestOptions: RequestOptions(path: '/test'),
          statusCode: 401,
          data: {'detail': 'No autorizado'},
        ),
      );

      final mapped = DioExceptionMapper.map(error);

      expect(mapped, isA<UnauthorizedException>());
      expect(mapped.message, 'No autorizado');
    });

    test('mapea 500 a ServerException', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/test'),
        type: DioExceptionType.badResponse,
        response: Response(
          requestOptions: RequestOptions(path: '/test'),
          statusCode: 500,
        ),
      );

      final mapped = DioExceptionMapper.map(error);

      expect(mapped, isA<ServerException>());
    });
  });
}
