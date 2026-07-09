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
                return _AppointmentTile(
                  clientId: client.userId,
                  appointment: appointment,
                );
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

class _AppointmentTile extends ConsumerStatefulWidget {
  const _AppointmentTile({
    required this.clientId,
    required this.appointment,
  });

  final String clientId;
  final AdminClientAppointment appointment;

  @override
  ConsumerState<_AppointmentTile> createState() => _AppointmentTileState();
}

class _AppointmentTileState extends ConsumerState<_AppointmentTile> {
  bool _isVoiding = false;

  @override
  Widget build(BuildContext context) {
    final appointment = widget.appointment;
    final localStart = appointment.scheduledStart.toLocal();
    final formatted =
        '${localStart.day.toString().padLeft(2, '0')}/'
        '${localStart.month.toString().padLeft(2, '0')}/'
        '${localStart.year} '
        '${localStart.hour.toString().padLeft(2, '0')}:'
        '${localStart.minute.toString().padLeft(2, '0')}';
    final canVoid = appointment.canBeVoidedByAdmin();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        ListTile(
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
        ),
        if (canVoid)
          Align(
            alignment: Alignment.centerRight,
            child: _isVoiding
                ? const SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : TextButton(
                    onPressed: _onVoidPressed,
                    child: const Text('Anular cita'),
                  ),
          ),
      ],
    );
  }

  Future<void> _onVoidPressed() async {
    final appointment = widget.appointment;
    final localStart = appointment.scheduledStart.toLocal();
    final formatted =
        '${localStart.day.toString().padLeft(2, '0')}/'
        '${localStart.month.toString().padLeft(2, '0')}/'
        '${localStart.year} '
        '${localStart.hour.toString().padLeft(2, '0')}:'
        '${localStart.minute.toString().padLeft(2, '0')}';

    final reason = await showDialog<String>(
      context: context,
      builder: (context) => _VoidAppointmentDialog(
        appointment: appointment,
        formattedDate: formatted,
      ),
    );

    if (reason == null || !mounted) return;

    setState(() => _isVoiding = true);
    final result = await ref.read(voidAdminAppointmentUseCaseProvider).call(
          VoidAdminAppointmentParams(
            appointmentId: appointment.id,
            reason: reason,
          ),
        );
    if (!mounted) return;
    setState(() => _isVoiding = false);

    result.when(
      success: (_) {
        ref.invalidate(_clientAppointmentsProvider(widget.clientId));
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Cita anulada correctamente')),
        );
      },
      error: (failure) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(failure.message)),
        );
      },
    );
  }
}

class _VoidAppointmentDialog extends StatefulWidget {
  const _VoidAppointmentDialog({
    required this.appointment,
    required this.formattedDate,
  });

  final AdminClientAppointment appointment;
  final String formattedDate;

  @override
  State<_VoidAppointmentDialog> createState() => _VoidAppointmentDialogState();
}

class _VoidAppointmentDialogState extends State<_VoidAppointmentDialog> {
  late final TextEditingController _reasonController;

  @override
  void initState() {
    super.initState();
    _reasonController = TextEditingController();
  }

  @override
  void dispose() {
    _reasonController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final reason = _reasonController.text.trim();
    final canSubmit = reason.length >= 3;

    return AlertDialog(
      title: const Text('Anular cita'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${widget.appointment.serviceName}\n'
            '${widget.appointment.barberDisplayName}\n'
            '${widget.formattedDate}',
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _reasonController,
            decoration: const InputDecoration(
              labelText: 'Motivo de anulación',
              hintText: 'Indica el motivo (mínimo 3 caracteres)',
              border: OutlineInputBorder(),
            ),
            maxLines: 3,
            maxLength: 500,
            onChanged: (_) => setState(() {}),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancelar'),
        ),
        FilledButton(
          onPressed: canSubmit ? () => Navigator.of(context).pop(reason) : null,
          child: const Text('Anular'),
        ),
      ],
    );
  }
}
