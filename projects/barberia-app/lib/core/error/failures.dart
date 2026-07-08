/// Fallos de dominio/aplicación independientes de frameworks.
sealed class Failure {
  const Failure(this.message);

  final String message;

  @override
  String toString() => message;
}

final class NetworkFailure extends Failure {
  const NetworkFailure([super.message = 'Error de conexión. Verifica tu red.']);
}

final class ServerFailure extends Failure {
  const ServerFailure([super.message = 'Error del servidor. Intenta más tarde.']);
}

final class UnauthorizedFailure extends Failure {
  const UnauthorizedFailure([super.message = 'Sesión no autorizada.']);
}

final class ValidationFailure extends Failure {
  const ValidationFailure(super.message);
}

final class UnknownFailure extends Failure {
  const UnknownFailure([super.message = 'Ocurrió un error inesperado.']);
}
