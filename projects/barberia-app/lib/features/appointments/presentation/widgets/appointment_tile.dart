import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../domain/entities/appointment_summary.dart';
import '../../domain/usecases/cancel_appointment_use_case.dart';
import '../providers/appointments_providers.dart';
import 'appointment_status_chip.dart';

class AppointmentTile extends ConsumerStatefulWidget {
  const AppointmentTile({
    super.key,
    required this.appointment,
    required this.isUpcoming,
  });

  final AppointmentSummary appointment;
  final bool isUpcoming;

  @override
  ConsumerState<AppointmentTile> createState() => _AppointmentTileState();
}

class _AppointmentTileState extends ConsumerState<AppointmentTile> {
  bool _isCancelling = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final now = DateTime.now();
    final localStart = widget.appointment.scheduledStart.toLocal();
    final dateFormat = DateFormat.yMMMEd('es');
    final timeFormat = DateFormat.Hm('es');
    final formattedDate =
        '${dateFormat.format(localStart)} · ${timeFormat.format(localStart)}';
    final canCancel = widget.isUpcoming &&
        widget.appointment.canBeCancelledByClient(now);

    return Opacity(
      opacity: widget.isUpcoming ? 1 : 0.85,
      child: Card(
        color: widget.isUpcoming
            ? null
            : theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
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
                          widget.appointment.serviceName,
                          style: theme.textTheme.titleMedium,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          widget.appointment.barberDisplayName,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          formattedDate,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),
                  ),
                  AppointmentStatusChip(
                    status: widget.appointment.status,
                    isUpcoming: widget.isUpcoming,
                  ),
                ],
              ),
              if (canCancel) ...[
                const SizedBox(height: 12),
                Align(
                  alignment: Alignment.centerRight,
                  child: _isCancelling
                      ? const SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : TextButton(
                          onPressed: _onCancelPressed,
                          child: const Text('Cancelar cita'),
                        ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _onCancelPressed() async {
    final localStart = widget.appointment.scheduledStart.toLocal();
    final dateFormat = DateFormat.yMMMEd('es');
    final timeFormat = DateFormat.Hm('es');
    final formattedDate =
        '${dateFormat.format(localStart)} · ${timeFormat.format(localStart)}';

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('¿Cancelar cita?'),
        content: Text(
          '${widget.appointment.serviceName}\n'
          '${widget.appointment.barberDisplayName}\n'
          '$formattedDate',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('No'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Sí, cancelar'),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    setState(() => _isCancelling = true);
    final result = await ref.read(cancelAppointmentUseCaseProvider).call(
          CancelAppointmentParams(widget.appointment.id),
        );
    if (!mounted) return;
    setState(() => _isCancelling = false);

    result.when(
      success: (_) {
        ref.invalidate(myAppointmentsProvider);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Cita cancelada correctamente')),
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
