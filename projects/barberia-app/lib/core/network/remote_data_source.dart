import 'package:dio/dio.dart';

import '../error/app_exception.dart';
import '../error/exception_mapper.dart';
import '../utils/result.dart';
import 'dio_safe_caller.dart';

/// Base para datasources remotos con manejo estandarizado de errores.
abstract class RemoteDataSource with DioSafeCaller {
  const RemoteDataSource(this.dio);

  final Dio dio;

  /// Ejecuta una petición y devuelve [Result] de dominio.
  Future<Result<T>> execute<T>(Future<T> Function() request) async {
    try {
      final data = await guard(request);
      return Success(data);
    } on AppException catch (error) {
      return Error(ExceptionMapper.toFailure(error));
    } catch (error) {
      return Error(ExceptionMapper.toFailure(error));
    }
  }
}
