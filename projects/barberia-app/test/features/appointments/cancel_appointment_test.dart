import 'package:barberia_app/core/utils/result.dart';
import 'package:barberia_app/features/appointments/data/models/appointment_dtos.dart';
import 'package:barberia_app/features/appointments/domain/entities/appointment_summary.dart';
import 'package:barberia_app/features/appointments/domain/repositories/appointments_repository.dart';
import 'package:barberia_app/features/appointments/presentation/pages/appointments_page.dart';
import 'package:barberia_app/features/appointments/presentation/providers/appointments_providers.dart';
import 'package:barberia_app/features/appointments/presentation/widgets/appointment_tile.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';

class _FakeAppointmentsRepository implements AppointmentsRepository {
  @override
  Future<Result<List<AppointmentSummary>>> listMyAppointments() async {
    return const Success([]);
  }

  @override
  Future<Result<AppointmentSummary>> cancelAppointment(
    String appointmentId,
  ) async {
    return Success(
      AppointmentSummary(
        id: appointmentId,
        status: 'cancelada',
        scheduledStart: DateTime.now().add(const Duration(days: 7)),
        scheduledEnd: DateTime.now().add(const Duration(days: 7, minutes: 30)),
        serviceName: 'Corte',
        barberDisplayName: 'Carlos',
      ),
    );
  }
}

void main() {
  setUpAll(() async {
    await initializeDateFormatting('es');
  });

  group('AppointmentSummary.canBeCancelledByClient', () {
    final now = DateTime(2026, 7, 15, 8, 0);

    test('permite cancelar cita confirmada con más de 2 horas', () {
      final appointment = AppointmentSummary(
        id: '1',
        status: 'confirmada',
        scheduledStart: now.add(const Duration(hours: 3)),
        scheduledEnd: now.add(const Duration(hours: 3, minutes: 30)),
        serviceName: 'Corte',
        barberDisplayName: 'Carlos',
      );

      expect(appointment.canBeCancelledByClient(now), isTrue);
    });

    test('rechaza cancelar con menos de 2 horas', () {
      final appointment = AppointmentSummary(
        id: '1',
        status: 'confirmada',
        scheduledStart: now.add(const Duration(hours: 1)),
        scheduledEnd: now.add(const Duration(hours: 1, minutes: 30)),
        serviceName: 'Corte',
        barberDisplayName: 'Carlos',
      );

      expect(appointment.canBeCancelledByClient(now), isFalse);
    });

    test('permite cancelar exactamente a las 2 horas', () {
      final appointment = AppointmentSummary(
        id: '1',
        status: 'confirmada',
        scheduledStart: now.add(const Duration(hours: 2)),
        scheduledEnd: now.add(const Duration(hours: 2, minutes: 30)),
        serviceName: 'Corte',
        barberDisplayName: 'Carlos',
      );

      expect(appointment.canBeCancelledByClient(now), isTrue);
    });

    test('rechaza estados no cancelables', () {
      final appointment = AppointmentSummary(
        id: '1',
        status: 'completada',
        scheduledStart: now.add(const Duration(hours: 5)),
        scheduledEnd: now.add(const Duration(hours: 5, minutes: 30)),
        serviceName: 'Corte',
        barberDisplayName: 'Carlos',
      );

      expect(appointment.canBeCancelledByClient(now), isFalse);
    });

    test('rechaza citas pasadas', () {
      final appointment = AppointmentSummary(
        id: '1',
        status: 'confirmada',
        scheduledStart: now.subtract(const Duration(hours: 1)),
        scheduledEnd: now.subtract(const Duration(minutes: 30)),
        serviceName: 'Corte',
        barberDisplayName: 'Carlos',
      );

      expect(appointment.canBeCancelledByClient(now), isFalse);
    });
  });

  test('AppointmentSummaryDto parsea respuesta de cancelación', () {
    final dto = AppointmentSummaryDto.fromJson({
      'id': '11111111-1111-1111-1111-111111111111',
      'status': 'cancelada',
      'scheduled_start': '2026-07-15T10:00:00-04:00',
      'scheduled_end': '2026-07-15T10:30:00-04:00',
      'service_name': 'Corte',
      'barber_display_name': 'Carlos',
    });

    expect(dto.toEntity().status, 'cancelada');
  });

  testWidgets('AppointmentTile muestra botón en cita cancelable', (tester) async {
    final appointment = AppointmentSummary(
      id: '11111111-1111-1111-1111-111111111111',
      status: 'confirmada',
      scheduledStart: DateTime.now().add(const Duration(days: 7)),
      scheduledEnd: DateTime.now().add(const Duration(days: 7, minutes: 30)),
      serviceName: 'Corte',
      barberDisplayName: 'Carlos',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          appointmentsRepositoryProvider.overrideWithValue(
            _FakeAppointmentsRepository(),
          ),
        ],
        child: MaterialApp(
          home: Scaffold(
            body: AppointmentTile(
              appointment: appointment,
              isUpcoming: true,
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Cancelar cita'), findsOneWidget);
  });

  testWidgets('AppointmentTile no muestra botón en cita pasada', (tester) async {
    final appointment = AppointmentSummary(
      id: '22222222-2222-2222-2222-222222222222',
      status: 'confirmada',
      scheduledStart: DateTime.now().subtract(const Duration(days: 1)),
      scheduledEnd: DateTime.now().subtract(const Duration(days: 1, minutes: -30)),
      serviceName: 'Corte',
      barberDisplayName: 'Carlos',
    );

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          home: Scaffold(
            body: AppointmentTile(
              appointment: appointment,
              isUpcoming: false,
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Cancelar cita'), findsNothing);
  });

  testWidgets('diálogo de confirmación cancela cita e invalida lista', (tester) async {
    final cancellable = AppointmentSummary(
      id: '11111111-1111-1111-1111-111111111111',
      status: 'confirmada',
      scheduledStart: DateTime.now().add(const Duration(days: 7)),
      scheduledEnd: DateTime.now().add(const Duration(days: 7, minutes: 30)),
      serviceName: 'Corte',
      barberDisplayName: 'Carlos',
    );

    var listLoadCount = 0;

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          appointmentsRepositoryProvider.overrideWithValue(
            _FakeAppointmentsRepository(),
          ),
          myAppointmentsProvider.overrideWith((ref) async {
            listLoadCount++;
            return [cancellable];
          }),
        ],
        child: const MaterialApp(
          home: Scaffold(
            body: AppointmentsPage(),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Cancelar cita'), findsOneWidget);

    await tester.tap(find.text('Cancelar cita'));
    await tester.pumpAndSettle();

    expect(find.text('¿Cancelar cita?'), findsOneWidget);

    await tester.tap(find.text('Sí, cancelar'));
    await tester.pumpAndSettle();

    expect(find.text('Cita cancelada correctamente'), findsOneWidget);
    expect(listLoadCount, greaterThan(1));
  });
}
