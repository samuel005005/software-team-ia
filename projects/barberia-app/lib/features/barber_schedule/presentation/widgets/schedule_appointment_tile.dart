import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../appointments/presentation/widgets/appointment_status_chip.dart';
import '../../domain/appointment_status_actions.dart';
import '../../domain/entities/barber_schedule_appointment.dart';
import '../../domain/usecases/update_barber_appointment_status_use_case.dart';
import '../providers/barber_schedule_providers.dart';

class ScheduleAppointmentTile extends ConsumerStatefulWidget {
  const ScheduleAppointmentTile({
    super.key,
    required this.appointment,
    required this.selectedDate,
  });

  final BarberScheduleAppointment appointment;
  final DateTime selectedDate;

  @override
  ConsumerState<ScheduleAppointmentTile> createState() =>
      _ScheduleAppointmentTileState();
}

class _ScheduleAppointmentTileState extends ConsumerState<ScheduleAppointmentTile> {
  bool _isUpdating = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final timeFormat = DateFormat.Hm('es');
    final localStart = widget.appointment.scheduledStart.toLocal();
    final localEnd = widget.appointment.scheduledEnd.toLocal();
    final timeRange =
        '${timeFormat.format(localStart)} – ${timeFormat.format(localEnd)}';
    final isCancelled = widget.appointment.status == 'cancelada';
    final now = DateTime.now();
    final actions = allowedBarberActions(
      currentStatus: widget.appointment.status,
      scheduledStart: widget.appointment.scheduledStart,
      now: now,
    );

    return Opacity(
      opacity: isCancelled ? 0.6 : 1,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          timeRange,
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          widget.appointment.clientDisplayName,
                          style: theme.textTheme.bodyLarge,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          widget.appointment.serviceName,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),
                  ),
                  AppointmentStatusChip(
                    status: widget.appointment.status,
                    isUpcoming: true,
                  ),
                ],
              ),
              if (actions.isNotEmpty) ...[
                const SizedBox(height: 12),
                if (_isUpdating)
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: SizedBox(
                      width: 24,
                      height: 24,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                  )
                else
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      for (final action in actions)
                        OutlinedButton(
                          onPressed: () => _onActionPressed(action),
                          child: Text(action.label),
                        ),
                    ],
                  ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _onActionPressed(BarberStatusAction action) async {
    if (_isUpdating) return;

    final needsConfirmation =
        action.targetStatus == 'no_show' || action.targetStatus == 'completada';

    if (needsConfirmation) {
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: Text(confirmationTitleFor(action.targetStatus)),
          content: Text(
            '${widget.appointment.clientDisplayName}\n'
            '${widget.appointment.serviceName}',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('Cancelar'),
            ),
            FilledButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text('Confirmar'),
            ),
          ],
        ),
      );

      if (confirmed != true || !mounted) return;
    }

    setState(() => _isUpdating = true);
    final result = await ref
        .read(updateBarberAppointmentStatusUseCaseProvider)
        .call(
          UpdateBarberAppointmentStatusParams(
            appointmentId: widget.appointment.id,
            status: action.targetStatus,
          ),
        );

    if (!mounted) return;
    setState(() => _isUpdating = false);

    final normalized = DateTime(
      widget.selectedDate.year,
      widget.selectedDate.month,
      widget.selectedDate.day,
    );

    result.when(
      success: (_) {
        ref.invalidate(barberScheduleProvider(normalized));
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(successMessageFor(action.targetStatus))),
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
