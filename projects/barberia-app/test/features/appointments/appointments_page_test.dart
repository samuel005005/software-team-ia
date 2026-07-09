import 'package:barberia_app/features/appointments/domain/entities/appointment_summary.dart';
import 'package:barberia_app/features/appointments/presentation/pages/appointments_page.dart';
import 'package:barberia_app/features/appointments/presentation/providers/appointments_providers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';

void main() {
  setUpAll(() async {
    await initializeDateFormatting('es');
  });

  final upcoming = AppointmentSummary(
    id: '11111111-1111-1111-1111-111111111111',
    status: 'confirmada',
    scheduledStart: DateTime.now().add(const Duration(days: 7)),
    scheduledEnd: DateTime.now().add(const Duration(days: 7, minutes: 30)),
    serviceName: 'Corte',
    barberDisplayName: 'Carlos',
  );

  final past = AppointmentSummary(
    id: '22222222-2222-2222-2222-222222222222',
    status: 'completada',
    scheduledStart: DateTime.now().subtract(const Duration(days: 14)),
    scheduledEnd: DateTime.now().subtract(const Duration(days: 14, minutes: -30)),
    serviceName: 'Barba',
    barberDisplayName: 'Luis',
  );

  testWidgets('AppointmentsPage muestra secciones Próximas y Pasadas', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          myAppointmentsProvider.overrideWith(
            (ref) async => [upcoming, past],
          ),
        ],
        child: const MaterialApp(
          home: AppointmentsPage(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Próximas'), findsOneWidget);
    expect(find.text('Pasadas'), findsOneWidget);
    expect(find.text('Corte'), findsOneWidget);
    expect(find.text('Barba'), findsOneWidget);
    expect(find.text('Carlos'), findsOneWidget);
    expect(find.text('Luis'), findsOneWidget);
    expect(find.text('Confirmada'), findsOneWidget);
    expect(find.text('Completada'), findsOneWidget);
  });

  testWidgets('AppointmentsPage muestra empty state sin citas', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          myAppointmentsProvider.overrideWith(
            (ref) async => <AppointmentSummary>[],
          ),
        ],
        child: const MaterialApp(
          home: AppointmentsPage(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Aún no tienes citas'), findsOneWidget);
    expect(find.text('Reservar cita'), findsOneWidget);
  });
}
