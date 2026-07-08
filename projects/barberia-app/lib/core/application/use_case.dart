import '../utils/result.dart';

/// Contrato base para casos de uso de la capa application.
abstract class UseCase<T, Params> {
  const UseCase();

  Future<Result<T>> call(Params params);
}

/// Parámetro vacío para casos de uso sin entrada.
final class NoParams {
  const NoParams();
}
