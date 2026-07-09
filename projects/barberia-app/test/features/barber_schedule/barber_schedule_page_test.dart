import 'dart:async';

import 'package:barberia_app/core/utils/result.dart';
import 'package:barberia_app/features/barber_schedule/domain/entities/barber_schedule_appointment.dart';
import 'package:barberia_app/features/barber_schedule/domain/repositories/barber_schedule_repository.dart';
import 'package:barberia_app/features/barber_schedule/domain/usecases/update_barber_appointment_status_use_case.dart';
import 'package:barberia_app/features/barber_schedule/presentation/pages/barber_schedule_page.dart';
import 'package:barberia_app/features/barber_schedule/presentation/providers/barber_schedule_providers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:intl/intl.dart';

class _FakeUpdateStatusUseCase extends UpdateBarberAppointmentStatusUseCase {
  _FakeUpdateStatusUseCase(this.onCall) : super(_ThrowingRepository());

  final void Function(UpdateBarberAppointmentStatusParams params) onCall;

  @override
  Future<Result<BarberScheduleAppointment>> call(
    UpdateBarberAppointmentStatusParams params,
  ) async {
    onCall(params);
    return Success(
      BarberScheduleAppointment(
        id: params.appointmentId,
        status: params.status,
        scheduledStart: DateTime(2026, 7, 9, 9, 0),
        scheduledEnd: DateTime(2026, 7, 9, 9, 30),
        serviceId: '22222222-2222-2222-2222-222222222222',
        serviceName: 'Corte',
        clientUserId: '33333333-3333-3333-3333-333333333333',
        clientDisplayName: 'Juan Pérez',
      ),
    );
  }
}

class _ThrowingRepository implements BarberScheduleRepository {
  @override
  Future<Result<List<BarberScheduleAppointment>>> getScheduleForDate({
    required DateTime date,
  }) {
    throw UnimplementedError();
  }

  @override
  Future<Result<BarberScheduleAppointment>> updateAppointmentStatus({
    required String appointmentId,
    required String status,
  }) {
    throw UnimplementedError();
  }
}

void main() {
  setUpAll(() async {
    await initializeDateFormatting('es');
  });

  BarberScheduleAppointment sampleAppointment({DateTime? scheduledStart}) {
    final start = scheduledStart ?? DateTime(2099, 7, 9, 9, 0);
    return BarberScheduleAppointment(
      id: '11111111-1111-1111-1111-111111111111',
      status: 'confirmada',
      scheduledStart: start,
      scheduledEnd: start.add(const Duration(minutes: 30)),
      serviceId: '22222222-2222-2222-2222-222222222222',
      serviceName: 'Corte',
      clientUserId: '33333333-3333-3333-3333-333333333333',
      clientDisplayName: 'Juan Pérez',
    );
  }

  testWidgets('BarberSchedulePage muestra loading inicial', (tester) async {
    final completer = Completer<List<BarberScheduleAppointment>>();
    final today = todayDateOnly();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          selectedScheduleDateProvider.overrideWith((ref) => today),
          barberScheduleProvider(today).overrideWith((ref) => completer.future),
        ],
        child: const MaterialApp(
          home: BarberSchedulePage(),
        ),
      ),
    );
    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('BarberSchedulePage muestra empty state', (tester) async {
    final today = todayDateOnly();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          selectedScheduleDateProvider.overrideWith((ref) => today),
          barberScheduleProvider(today).overrideWith((ref) async => []),
        ],
        child: const MaterialApp(
          home: BarberSchedulePage(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('No tienes citas este día'), findsOneWidget);
  });

  testWidgets('BarberSchedulePage muestra tile con datos', (tester) async {
    final today = todayDateOnly();
    final appointment = sampleAppointment();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          selectedScheduleDateProvider.overrideWith((ref) => today),
          barberScheduleProvider(today).overrideWith(
            (ref) async => [appointment],
          ),
        ],
        child: const MaterialApp(
          home: BarberSchedulePage(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    final timeFormat = DateFormat.Hm('es');
    final timeRange =
        '${timeFormat.format(appointment.scheduledStart)} – ${timeFormat.format(appointment.scheduledEnd)}';

    expect(find.text(timeRange), findsOneWidget);
    expect(find.text('Juan Pérez'), findsOneWidget);
    expect(find.text('Corte'), findsOneWidget);
    expect(find.text('Confirmada'), findsOneWidget);
    expect(find.text('Iniciar'), findsOneWidget);
  });

  testWidgets('Tile confirmada muestra botón Iniciar', (tester) async {
    final today = todayDateOnly();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          selectedScheduleDateProvider.overrideWith((ref) => today),
          barberScheduleProvider(today).overrideWith(
            (ref) async => [sampleAppointment()],
          ),
        ],
        child: const MaterialApp(
          home: BarberSchedulePage(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Iniciar'), findsOneWidget);
    expect(find.text('No asistió'), findsNothing);
  });

  testWidgets('Tile completada no muestra botones de acción', (tester) async {
    final today = todayDateOnly();
    final appointment = BarberScheduleAppointment(
      id: '11111111-1111-1111-1111-111111111111',
      status: 'completada',
      scheduledStart: DateTime(2026, 7, 9, 9, 0),
      scheduledEnd: DateTime(2026, 7, 9, 9, 30),
      serviceId: '22222222-2222-2222-2222-222222222222',
      serviceName: 'Corte',
      clientUserId: '33333333-3333-3333-3333-333333333333',
      clientDisplayName: 'Juan Pérez',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          selectedScheduleDateProvider.overrideWith((ref) => today),
          barberScheduleProvider(today).overrideWith(
            (ref) async => [appointment],
          ),
        ],
        child: const MaterialApp(
          home: BarberSchedulePage(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Iniciar'), findsNothing);
    expect(find.text('Completar'), findsNothing);
    expect(find.text('No asistió'), findsNothing);
  });

  testWidgets('Tap Iniciar invoca use case y muestra snackbar', (tester) async {
    final today = todayDateOnly();
    final appointment = sampleAppointment();
    UpdateBarberAppointmentStatusParams? capturedParams;

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          selectedScheduleDateProvider.overrideWith((ref) => today),
          barberScheduleProvider(today).overrideWith(
            (ref) async => [appointment],
          ),
          updateBarberAppointmentStatusUseCaseProvider.overrideWith(
            (ref) => _FakeUpdateStatusUseCase((params) {
              capturedParams = params;
            }),
          ),
        ],
        child: const MaterialApp(
          home: Scaffold(
            body: BarberSchedulePage(),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.text('Iniciar'));
    await tester.pumpAndSettle();

    expect(capturedParams?.appointmentId, appointment.id);
    expect(capturedParams?.status, 'en_progreso');
    expect(find.text('Cita iniciada'), findsOneWidget);
  });

  testWidgets('Botón Hoy resetea la fecha seleccionada', (tester) async {
    final today = todayDateOnly();
    final pastDate = today.subtract(const Duration(days: 5));
    final dateFormat = DateFormat.yMMMEd('es');

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          selectedScheduleDateProvider.overrideWith((ref) => pastDate),
          barberScheduleProvider(pastDate).overrideWith((ref) async => []),
          barberScheduleProvider(today).overrideWith((ref) async => []),
        ],
        child: const MaterialApp(
          home: BarberSchedulePage(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text(dateFormat.format(pastDate)), findsOneWidget);

    await tester.tap(find.text('Hoy'));
    await tester.pumpAndSettle();

    expect(find.text(dateFormat.format(today)), findsOneWidget);
  });

  testWidgets('Botón Mañana avanza un día', (tester) async {
    final today = todayDateOnly();
    final tomorrow = today.add(const Duration(days: 1));
    final dateFormat = DateFormat.yMMMEd('es');

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          selectedScheduleDateProvider.overrideWith((ref) => today),
          barberScheduleProvider(today).overrideWith((ref) async => []),
          barberScheduleProvider(tomorrow).overrideWith((ref) async => []),
        ],
        child: const MaterialApp(
          home: BarberSchedulePage(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text(dateFormat.format(today)), findsOneWidget);

    await tester.tap(find.text('Mañana'));
    await tester.pumpAndSettle();

    expect(find.text(dateFormat.format(tomorrow)), findsOneWidget);
  });
}
