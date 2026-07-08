import 'package:barberia_app/core/error/failures.dart';
import 'package:barberia_app/core/network/remote_data_source.dart';
import 'package:barberia_app/core/utils/result.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';

class _TestRemoteDataSource extends RemoteDataSource {
  const _TestRemoteDataSource(super.dio);
}

void main() {
  group('RemoteDataSource', () {
    test('execute retorna Success en petición exitosa', () async {
      final dio = Dio();
      dio.httpClientAdapter = _SuccessAdapter();
      final dataSource = _TestRemoteDataSource(dio);

      final result = await dataSource.execute(() async => 'ok');

      expect(result, isA<Success<String>>());
      expect((result as Success<String>).value, 'ok');
    });

    test('execute retorna Error en fallo de red', () async {
      final dio = Dio();
      dio.httpClientAdapter = _ErrorAdapter();
      final dataSource = _TestRemoteDataSource(dio);

      final result = await dataSource.execute(() => dio.get<dynamic>('/fail'));

      expect(result.isError, isTrue);
      expect(result, isA<Error<dynamic>>());
      expect((result as Error).failure, isA<NetworkFailure>());
    });
  });
}

class _SuccessAdapter implements HttpClientAdapter {
  @override
  void close({bool force = false}) {}

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<List<int>>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    return ResponseBody.fromString('{"ok":true}', 200);
  }
}

class _ErrorAdapter implements HttpClientAdapter {
  @override
  void close({bool force = false}) {}

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<List<int>>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    throw DioException(
      requestOptions: options,
      type: DioExceptionType.connectionError,
    );
  }
}
