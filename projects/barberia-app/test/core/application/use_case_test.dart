import 'package:barberia_app/core/application/use_case.dart';
import 'package:barberia_app/core/error/failures.dart';
import 'package:barberia_app/core/utils/result.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('Result', () {
    test('when ejecuta rama success', () {
      const result = Success<int>(10);

      final value = result.when(
        success: (v) => v,
        error: (_) => -1,
      );

      expect(value, 10);
    });

    test('when ejecuta rama error', () {
      const result = Error<int>(UnknownFailure('fallo'));

      final value = result.when(
        success: (_) => 'ok',
        error: (f) => f.message,
      );

      expect(value, 'fallo');
    });
  });

  group('UseCase', () {
    test('NoParams es constante reutilizable', () {
      expect(identical(const NoParams(), const NoParams()), isTrue);
    });
  });
}
