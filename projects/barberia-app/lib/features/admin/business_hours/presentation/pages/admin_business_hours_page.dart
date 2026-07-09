import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../../app/providers/app_state_providers.dart';
import '../../domain/entities/business_hours_day.dart';
import '../../domain/usecases/admin_business_hours_use_cases.dart';
import '../providers/admin_business_hours_providers.dart';

class AdminBusinessHoursPage extends ConsumerStatefulWidget {
  const AdminBusinessHoursPage({super.key});

  @override
  ConsumerState<AdminBusinessHoursPage> createState() =>
      _AdminBusinessHoursPageState();
}

class _AdminBusinessHoursPageState extends ConsumerState<AdminBusinessHoursPage> {
  List<BusinessHoursDay>? _draftDays;
  bool _isSaving = false;

  @override
  Widget build(BuildContext context) {
    final hoursAsync = ref.watch(adminBusinessHoursProvider);

    return hoursAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(error.toString()),
              const SizedBox(height: 16),
              FilledButton(
                onPressed: () => ref.invalidate(adminBusinessHoursProvider),
                child: const Text('Reintentar'),
              ),
            ],
          ),
        ),
      ),
      data: (days) {
        final draft = _draftDays ?? days;

        return Stack(
          children: [
            ListView.separated(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
              itemCount: draft.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final day = draft[index];
                return _BusinessHoursDayCard(
                  day: day,
                  onClosedChanged: (isClosed) {
                    setState(() {
                      _draftDays = _replaceDay(
                        draft,
                        day.copyWith(isClosed: isClosed),
                      );
                    });
                  },
                  onOpenTimeChanged: (openTime) {
                    setState(() {
                      _draftDays = _replaceDay(
                        draft,
                        day.copyWith(openTime: openTime),
                      );
                    });
                  },
                  onCloseTimeChanged: (closeTime) {
                    setState(() {
                      _draftDays = _replaceDay(
                        draft,
                        day.copyWith(closeTime: closeTime),
                      );
                    });
                  },
                );
              },
            ),
            Positioned(
              left: 16,
              right: 16,
              bottom: 16,
              child: FilledButton.icon(
                onPressed: _isSaving ? null : () => _save(context, draft),
                icon: _isSaving
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.save_outlined),
                label: const Text('Guardar horario'),
              ),
            ),
          ],
        );
      },
    );
  }

  List<BusinessHoursDay> _replaceDay(
    List<BusinessHoursDay> days,
    BusinessHoursDay updated,
  ) {
    return days
        .map((day) => day.weekday == updated.weekday ? updated : day)
        .toList();
  }

  Future<void> _save(BuildContext context, List<BusinessHoursDay> days) async {
    setState(() => _isSaving = true);
    ref.read(appStateProvider.notifier).setGlobalLoading(true);

    final result = await ref.read(updateAdminBusinessHoursUseCaseProvider).call(
          UpdateAdminBusinessHoursParams(days: days),
        );

    ref.read(appStateProvider.notifier).setGlobalLoading(false);
    if (!mounted) return;

    setState(() => _isSaving = false);
    result.when(
      success: (savedDays) {
        setState(() => _draftDays = savedDays);
        ref.invalidate(adminBusinessHoursProvider);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Horario del local actualizado')),
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

class _BusinessHoursDayCard extends StatelessWidget {
  const _BusinessHoursDayCard({
    required this.day,
    required this.onClosedChanged,
    required this.onOpenTimeChanged,
    required this.onCloseTimeChanged,
  });

  final BusinessHoursDay day;
  final ValueChanged<bool> onClosedChanged;
  final ValueChanged<String> onOpenTimeChanged;
  final ValueChanged<String> onCloseTimeChanged;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              BusinessHoursDay.weekdayLabel(day.weekday),
              style: Theme.of(context).textTheme.titleMedium,
            ),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Día cerrado'),
              value: day.isClosed,
              onChanged: onClosedChanged,
            ),
            if (!day.isClosed) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: _TimeField(
                      label: 'Apertura',
                      value: day.openTime,
                      onChanged: onOpenTimeChanged,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _TimeField(
                      label: 'Cierre',
                      value: day.closeTime,
                      onChanged: onCloseTimeChanged,
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _TimeField extends StatelessWidget {
  const _TimeField({
    required this.label,
    required this.value,
    required this.onChanged,
  });

  final String label;
  final String value;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    final time = _parseTime(value);

    return OutlinedButton(
      onPressed: () async {
        final picked = await showTimePicker(
          context: context,
          initialTime: time,
        );
        if (picked == null) return;
        onChanged(_formatTime(picked));
      },
      child: Align(
        alignment: Alignment.centerLeft,
        child: Text('$label: ${_formatDisplay(time)}'),
      ),
    );
  }

  static TimeOfDay _parseTime(String raw) {
    final parts = raw.split(':');
    final hour = int.tryParse(parts.first) ?? 9;
    final minute = parts.length > 1 ? int.tryParse(parts[1]) ?? 0 : 0;
    return TimeOfDay(hour: hour, minute: minute);
  }

  static String _formatTime(TimeOfDay time) {
    final hour = time.hour.toString().padLeft(2, '0');
    final minute = time.minute.toString().padLeft(2, '0');
    return '$hour:$minute:00';
  }

  static String _formatDisplay(TimeOfDay time) {
    final hour = time.hour.toString().padLeft(2, '0');
    final minute = time.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }
}
