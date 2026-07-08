import 'package:dio/dio.dart';

import 'dio_exception_mapper.dart';

/// Ejecuta una petición HTTP y normaliza errores de Dio.
mixin DioSafeCaller {
  Future<T> guard<T>(Future<T> Function() request) async {
    try {
      return await request();
    } on DioException catch (error) {
      throw DioExceptionMapper.map(error);
    }
  }
}
