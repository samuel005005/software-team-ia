import 'package:barberia_app/features/client_booking/presentation/pages/book_appointment_page.dart';
import 'package:barberia_app/features/services/domain/entities/service_item.dart';
import 'package:barberia_app/features/services/presentation/providers/services_providers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const service = ServiceItem(
    id: '11111111-1111-1111-1111-111111111111',
    name: 'Corte clásico',
    durationMinutes: 30,
    priceDop: '400.00',
    description: 'Incluye lavado',
  );

  testWidgets('BookAppointmentPage renderiza wizard de 4 pasos', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          activeServicesProvider.overrideWith(
            (ref) async => [service],
          ),
        ],
        child: const MaterialApp(
          home: BookAppointmentPage(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Servicio'), findsOneWidget);
    expect(find.text('Barbero'), findsOneWidget);
    expect(find.text('Fecha y hora'), findsOneWidget);
    expect(find.text('Confirmar'), findsOneWidget);
    expect(find.text('Siguiente'), findsOneWidget);
  });

  testWidgets('pre-selección de servicio vía initialServiceId', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          activeServicesProvider.overrideWith(
            (ref) async => [service],
          ),
        ],
        child: const MaterialApp(
          home: BookAppointmentPage(
            initialServiceId: '11111111-1111-1111-1111-111111111111',
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Corte clásico'), findsOneWidget);
    expect(find.byIcon(Icons.check_circle), findsOneWidget);
  });

  testWidgets('Siguiente deshabilitado sin selección de servicio', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          activeServicesProvider.overrideWith(
            (ref) async => [service],
          ),
        ],
        child: const MaterialApp(
          home: BookAppointmentPage(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    final nextButton = tester.widget<FilledButton>(
      find.widgetWithText(FilledButton, 'Siguiente'),
    );
    expect(nextButton.onPressed, isNull);
  });

  testWidgets('Siguiente habilitado tras seleccionar servicio', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          activeServicesProvider.overrideWith(
            (ref) async => [service],
          ),
        ],
        child: const MaterialApp(
          home: BookAppointmentPage(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.text('Corte clásico'));
    await tester.pumpAndSettle();

    final nextButton = tester.widget<FilledButton>(
      find.widgetWithText(FilledButton, 'Siguiente'),
    );
    expect(nextButton.onPressed, isNotNull);
  });
}
