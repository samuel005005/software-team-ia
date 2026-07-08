import 'app_exception.dart';
import 'failures.dart';

/// Convierte excepciones de infraestructura en fallos de dominio.
abstract final class ExceptionMapper {
  static Failure toFailure(Object error) {
    return switch (error) {
      NetworkException(:final message) => NetworkFailure(message),
      ServerException(:final message) => ServerFailure(message),
      UnauthorizedException(:final message) => UnauthorizedFailure(message),
      ValidationException(:final message) => ValidationFailure(message),
      AppException(:final message) => UnknownFailure(message),
      _ => UnknownFailure(error.toString()),
    };
  }
}
