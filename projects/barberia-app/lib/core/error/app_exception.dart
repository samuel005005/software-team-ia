/// Excepción interna de la capa de datos/infraestructura.
sealed class AppException implements Exception {
  const AppException(this.message);

  final String message;

  @override
  String toString() => message;
}

final class NetworkException extends AppException {
  const NetworkException(super.message);
}

final class ServerException extends AppException {
  const ServerException(super.message, {this.statusCode});

  final int? statusCode;
}

final class UnauthorizedException extends AppException {
  const UnauthorizedException(super.message);
}

final class ValidationException extends AppException {
  const ValidationException(super.message);
}

final class ConfigurationException extends AppException {
  const ConfigurationException(super.message);
}
