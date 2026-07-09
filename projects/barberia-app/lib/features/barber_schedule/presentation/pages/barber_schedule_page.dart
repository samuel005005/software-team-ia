import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/barber_schedule_providers.dart';
import '../widgets/schedule_appointment_tile.dart';
import '../widgets/schedule_date_header.dart';

class BarberSchedulePage extends ConsumerWidget {
  const BarberSchedulePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedDate = ref.watch(selectedScheduleDateProvider);
    final normalized = DateTime(
      selectedDate.year,
      selectedDate.month,
      selectedDate.day,
    );
    final scheduleAsync = ref.watch(barberScheduleProvider(normalized));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
          child: ScheduleDateHeader(
            selectedDate: normalized,
            onDateChanged: (date) {
              ref.read(selectedScheduleDateProvider.notifier).state = DateTime(
                date.year,
                date.month,
                date.day,
              );
            },
          ),
        ),
        const SizedBox(height: 8),
        Expanded(
          child: scheduleAsync.when(
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
                      onPressed: () =>
                          ref.invalidate(barberScheduleProvider(normalized)),
                      child: const Text('Reintentar'),
                    ),
                  ],
                ),
              ),
            ),
            data: (appointments) {
              if (appointments.isEmpty) {
                return const Center(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: Text('No tienes citas este día'),
                  ),
                );
              }

              return RefreshIndicator(
                onRefresh: () async {
                  ref.invalidate(barberScheduleProvider(normalized));
                  await ref.read(barberScheduleProvider(normalized).future);
                },
                child: ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: appointments.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 12),
                  itemBuilder: (context, index) {
                    return ScheduleAppointmentTile(
                      appointment: appointments[index],
                      selectedDate: normalized,
                    );
                  },
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
