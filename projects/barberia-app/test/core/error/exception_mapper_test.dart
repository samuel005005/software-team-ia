import 'package:barberia_app/core/error/app_exception.dart';
import 'package:barberia_app/core/error/exception_mapper.dart';
import 'package:barberia_app/core/error/failures.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('ExceptionMapper', () {
    test('mapea NetworkException a NetworkFailure', () {
      const exception = NetworkException('sin red');

      final failure = ExceptionMapper.toFailure(exception);

      expect(failure, isA<NetworkFailure>());
      expect(failure.message, 'sin red');
    });

    test('mapea UnauthorizedException a UnauthorizedFailure', () {
      const exception = UnauthorizedException('token inválido');

      final failure = ExceptionMapper.toFailure(exception);

      expect(failure, isA<UnauthorizedFailure>());
    });

    test('mapea errores desconocidos a UnknownFailure', () {
      final failure = ExceptionMapper.toFailure(Exception('boom'));

      expect(failure, isA<UnknownFailure>());
    });
  });
}
