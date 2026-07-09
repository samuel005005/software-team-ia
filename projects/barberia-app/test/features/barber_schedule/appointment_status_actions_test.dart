import 'package:barberia_app/features/barber_schedule/domain/appointment_status_actions.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  final pastStart = DateTime(2020, 1, 1, 10, 0);
  final futureStart = DateTime(2099, 1, 1, 10, 0);
  final now = DateTime(2025, 6, 1, 12, 0);

  group('allowedBarberActions', () {
    test('pendiente muestra Confirmar y No asistió si hora pasó', () {
      final actions = allowedBarberActions(
        currentStatus: 'pendiente',
        scheduledStart: pastStart,
        now: now,
      );

      expect(actions.map((a) => a.label).toList(), ['Confirmar', 'No asistió']);
    });

    test('pendiente oculta No asistió antes de hora inicio', () {
      final actions = allowedBarberActions(
        currentStatus: 'pendiente',
        scheduledStart: futureStart,
        now: now,
      );

      expect(actions.map((a) => a.label).toList(), ['Confirmar']);
    });

    test('confirmada muestra Iniciar', () {
      final actions = allowedBarberActions(
        currentStatus: 'confirmada',
        scheduledStart: futureStart,
        now: now,
      );

      expect(actions.map((a) => a.label).toList(), ['Iniciar']);
    });

    test('confirmada muestra No asistió si hora pasó', () {
      final actions = allowedBarberActions(
        currentStatus: 'confirmada',
        scheduledStart: pastStart,
        now: now,
      );

      expect(actions.map((a) => a.label).toList(), ['Iniciar', 'No asistió']);
    });

    test('en_progreso muestra Completar', () {
      final actions = allowedBarberActions(
        currentStatus: 'en_progreso',
        scheduledStart: pastStart,
        now: now,
      );

      expect(actions.map((a) => a.label).toList(), ['Completar']);
    });

    test('completada no muestra acciones', () {
      final actions = allowedBarberActions(
        currentStatus: 'completada',
        scheduledStart: pastStart,
        now: now,
      );

      expect(actions, isEmpty);
    });

    test('cancelada no muestra acciones', () {
      final actions = allowedBarberActions(
        currentStatus: 'cancelada',
        scheduledStart: pastStart,
        now: now,
      );

      expect(actions, isEmpty);
    });

    test('no_show no muestra acciones', () {
      final actions = allowedBarberActions(
        currentStatus: 'no_show',
        scheduledStart: pastStart,
        now: now,
      );

      expect(actions, isEmpty);
    });
  });
}
