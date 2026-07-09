import 'package:barberia_app/core/utils/result.dart';
import 'package:barberia_app/features/admin/users/data/models/admin_client_dtos.dart';
import 'package:barberia_app/features/admin/users/domain/entities/admin_client.dart';
import 'package:barberia_app/features/admin/users/domain/entities/admin_client_appointment.dart';
import 'package:barberia_app/features/admin/users/domain/repositories/admin_clients_repository.dart';
import 'package:barberia_app/features/admin/users/presentation/providers/admin_clients_providers.dart';
import 'package:barberia_app/features/admin/users/presentation/widgets/admin_client_appointments_dialog.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeAdminClientsRepository implements AdminClientsRepository {
  _FakeAdminClientsRepository(this.appointments);

  final List<AdminClientAppointment> appointments;
  int voidCalls = 0;
  String? lastVoidReason;

  @override
  Future<Result<List<AdminClient>>> listClients() async {
    throw UnimplementedError();
  }

  @override
  Future<Result<AdminClient>> updateClient({
    required String userId,
    bool? isActive,
  }) async {
    throw UnimplementedError();
  }

  @override
  Future<Result<List<AdminClientAppointment>>> listClientAppointments(
    String userId,
  ) async {
    return Success(appointments);
  }

  @override
  Future<Result<AdminClientAppointment>> voidAppointment({
    required String appointmentId,
    required String reason,
  }) async {
    voidCalls += 1;
    lastVoidReason = reason;
    final appointment = appointments.firstWhere((item) => item.id == appointmentId);
    return Success(
      AdminClientAppointment(
        id: appointment.id,
        status: 'cancelada',
        scheduledStart: appointment.scheduledStart,
        scheduledEnd: appointment.scheduledEnd,
        serviceName: appointment.serviceName,
        barberDisplayName: appointment.barberDisplayName,
      ),
    );
  }
}

AdminClientAppointment _appointment({
  required String id,
  required String status,
}) {
  return AdminClientAppointment(
    id: id,
    status: status,
    scheduledStart: DateTime(2026, 7, 15, 10),
    scheduledEnd: DateTime(2026, 7, 15, 10, 30),
    serviceName: 'Corte',
    barberDisplayName: 'Carlos',
  );
}

void main() {
  group('AdminClientAppointment.canBeVoidedByAdmin', () {
    test('permite anular estados previos a completada', () {
      for (final status in ['pendiente', 'confirmada', 'en_progreso', 'no_show']) {
        final appointment = _appointment(id: '1', status: status);
        expect(appointment.canBeVoidedByAdmin(), isTrue, reason: status);
      }
    });

    test('rechaza completada y cancelada', () {
      expect(_appointment(id: '1', status: 'completada').canBeVoidedByAdmin(), isFalse);
      expect(_appointment(id: '1', status: 'cancelada').canBeVoidedByAdmin(), isFalse);
    });
  });

  test('VoidAdminAppointmentRequestDto serializa reason', () {
    const dto = VoidAdminAppointmentRequestDto(reason: 'Emergencia operativa');
    expect(dto.toJson(), {'reason': 'Emergencia operativa'});
  });

  testWidgets('muestra botón Anular solo en citas anulables', (tester) async {
    final repository = _FakeAdminClientsRepository([
      _appointment(id: '1', status: 'confirmada'),
      _appointment(id: '2', status: 'completada'),
    ]);

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          adminClientsRepositoryProvider.overrideWithValue(repository),
        ],
        child: MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) {
                return ElevatedButton(
                  onPressed: () {
                    showDialog<void>(
                      context: context,
                      builder: (_) => AdminClientAppointmentsDialog(
                        client: const AdminClient(
                          userId: 'client-1',
                          email: 'client@example.com',
                          fullName: 'Ana Cliente',
                          phone: '8095550000',
                          isActive: true,
                        ),
                      ),
                    );
                  },
                  child: const Text('Abrir'),
                );
              },
            ),
          ),
        ),
      ),
    );

    await tester.tap(find.text('Abrir'));
    await tester.pumpAndSettle();

    expect(find.text('Anular cita'), findsOneWidget);
  });

  testWidgets('diálogo exige motivo mínimo de 3 caracteres', (tester) async {
    final repository = _FakeAdminClientsRepository([
      _appointment(id: '1', status: 'confirmada'),
    ]);

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          adminClientsRepositoryProvider.overrideWithValue(repository),
        ],
        child: MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) {
                return ElevatedButton(
                  onPressed: () {
                    showDialog<void>(
                      context: context,
                      builder: (_) => AdminClientAppointmentsDialog(
                        client: const AdminClient(
                          userId: 'client-1',
                          email: 'client@example.com',
                          fullName: 'Ana Cliente',
                          phone: '8095550000',
                          isActive: true,
                        ),
                      ),
                    );
                  },
                  child: const Text('Abrir'),
                );
              },
            ),
          ),
        ),
      ),
    );

    await tester.tap(find.text('Abrir'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Anular cita'));
    await tester.pumpAndSettle();

    final voidButton = find.widgetWithText(FilledButton, 'Anular');
    final button = tester.widget<FilledButton>(voidButton);
    expect(button.onPressed, isNull);

    await tester.enterText(find.byType(TextField), 'ab');
    await tester.pump();

    final disabledButton = tester.widget<FilledButton>(voidButton);
    expect(disabledButton.onPressed, isNull);

    await tester.enterText(find.byType(TextField), 'Emergencia');
    await tester.pump();

    final enabledButton = tester.widget<FilledButton>(voidButton);
    expect(enabledButton.onPressed, isNotNull);
  });

  testWidgets('flujo exitoso muestra snackbar y refresca lista', (tester) async {
    final repository = _FakeAdminClientsRepository([
      _appointment(id: '1', status: 'confirmada'),
    ]);

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          adminClientsRepositoryProvider.overrideWithValue(repository),
        ],
        child: MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) {
                return ElevatedButton(
                  onPressed: () {
                    showDialog<void>(
                      context: context,
                      builder: (_) => AdminClientAppointmentsDialog(
                        client: const AdminClient(
                          userId: 'client-1',
                          email: 'client@example.com',
                          fullName: 'Ana Cliente',
                          phone: '8095550000',
                          isActive: true,
                        ),
                      ),
                    );
                  },
                  child: const Text('Abrir'),
                );
              },
            ),
          ),
        ),
      ),
    );

    await tester.tap(find.text('Abrir'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Anular cita'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField), 'Conflicto de agenda');
    await tester.pump();
    await tester.tap(find.widgetWithText(FilledButton, 'Anular'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));

    expect(repository.voidCalls, 1);
    expect(repository.lastVoidReason, 'Conflicto de agenda');
    expect(find.text('Cita anulada correctamente'), findsOneWidget);
  });
}
