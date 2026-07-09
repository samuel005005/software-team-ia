import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../providers/barber_schedule_providers.dart';

class ScheduleDateHeader extends StatelessWidget {
  const ScheduleDateHeader({
    super.key,
    required this.selectedDate,
    required this.onDateChanged,
  });

  final DateTime selectedDate;
  final ValueChanged<DateTime> onDateChanged;

  DateTime get _today => todayDateOnly();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final dateFormat = DateFormat.yMMMEd('es');
    final formattedDate = dateFormat.format(selectedDate);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            FilledButton.tonal(
              onPressed: () => onDateChanged(_today),
              child: const Text('Hoy'),
            ),
            const SizedBox(width: 8),
            FilledButton.tonal(
              onPressed: () => onDateChanged(_today.add(const Duration(days: 1))),
              child: const Text('Mañana'),
            ),
            const Spacer(),
            IconButton(
              tooltip: 'Elegir fecha',
              onPressed: () => _pickDate(context),
              icon: const Icon(Icons.calendar_today),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            IconButton(
              tooltip: 'Día anterior',
              onPressed: () => onDateChanged(
                selectedDate.subtract(const Duration(days: 1)),
              ),
              icon: const Icon(Icons.chevron_left),
            ),
            Expanded(
              child: Text(
                formattedDate,
                textAlign: TextAlign.center,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            IconButton(
              tooltip: 'Día siguiente',
              onPressed: () => onDateChanged(
                selectedDate.add(const Duration(days: 1)),
              ),
              icon: const Icon(Icons.chevron_right),
            ),
          ],
        ),
      ],
    );
  }

  Future<void> _pickDate(BuildContext context) async {
    final today = _today;
    final picked = await showDatePicker(
      context: context,
      initialDate: selectedDate,
      firstDate: today.subtract(const Duration(days: 90)),
      lastDate: today.add(const Duration(days: 90)),
      locale: const Locale('es'),
    );
    if (picked != null) {
      onDateChanged(DateTime(picked.year, picked.month, picked.day));
    }
  }
}
