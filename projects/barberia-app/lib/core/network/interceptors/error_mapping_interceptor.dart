import 'package:dio/dio.dart';

import '../dio_exception_mapper.dart';

/// Normaliza errores de Dio a excepciones internas de la app.
class ErrorMappingInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    handler.reject(
      err.copyWith(error: DioExceptionMapper.map(err)),
    );
  }
}
