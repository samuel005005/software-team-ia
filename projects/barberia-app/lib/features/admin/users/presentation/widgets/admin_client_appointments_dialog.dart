import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/admin_client.dart';
import '../../domain/entities/admin_client_appointment.dart';
import '../../domain/usecases/admin_clients_use_cases.dart';
import '../providers/admin_clients_providers.dart';

class AdminClientAppointmentsDialog extends ConsumerWidget {
  const AdminClientAppointmentsDialog({super.key, required this.client});

  final AdminClient client;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appointmentsAsync = ref.watch(_clientAppointmentsProvider(client.userId));

    return AlertDialog(
      title: Text('Citas — ${client.fullName}'),
      content: SizedBox(
        width: double.maxFinite,
        child: appointmentsAsync.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, _) => Text(error.toString()),
          data: (appointments) {
            if (appointments.isEmpty) {
              return const Text('Este cliente no tiene citas registradas.');
            }

            return ListView.separated(
              shrinkWrap: true,
              itemCount: appointments.length,
              separatorBuilder: (_, __) => const Divider(),
              itemBuilder: (context, index) {
                final appointment = appointments[index];
                return _AppointmentTile(appointment: appointment);
              },
            );
          },
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cerrar'),
        ),
      ],
    );
  }
}

final _clientAppointmentsProvider =
    FutureProvider.autoDispose.family<List<AdminClientAppointment>, String>(
  (ref, userId) async {
    final result = await ref.watch(listClientAppointmentsUseCaseProvider).call(
          ListClientAppointmentsParams(userId),
        );
    return result.when(
      success: (appointments) => appointments,
      error: (failure) => throw failure,
    );
  },
);

class _AppointmentTile extends StatelessWidget {
  const _AppointmentTile({required this.appointment});

  final AdminClientAppointment appointment;

  @override
  Widget build(BuildContext context) {
    final localStart = appointment.scheduledStart.toLocal();
    final formatted =
        '${localStart.day.toString().padLeft(2, '0')}/'
        '${localStart.month.toString().padLeft(2, '0')}/'
        '${localStart.year} '
        '${localStart.hour.toString().padLeft(2, '0')}:'
        '${localStart.minute.toString().padLeft(2, '0')}';

    return ListTile(
      contentPadding: EdgeInsets.zero,
      title: Text(appointment.serviceName),
      subtitle: Text(
        '${appointment.barberDisplayName}\n$formatted',
      ),
      isThreeLine: true,
      trailing: Chip(
        label: Text(appointment.status),
        visualDensity: VisualDensity.compact,
      ),
    );
  }
}
