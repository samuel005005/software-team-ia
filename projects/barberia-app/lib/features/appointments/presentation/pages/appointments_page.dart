import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../app/router/routes.dart';
import '../providers/appointments_providers.dart';
import '../widgets/appointment_tile.dart';

class AppointmentsPage extends ConsumerWidget {
  const AppointmentsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appointmentsAsync = ref.watch(myAppointmentsProvider);

    return appointmentsAsync.when(
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
                onPressed: () => ref.invalidate(myAppointmentsProvider),
                child: const Text('Reintentar'),
              ),
            ],
          ),
        ),
      ),
      data: (appointments) {
        if (appointments.isEmpty) {
          return Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('Aún no tienes citas'),
                  const SizedBox(height: 16),
                  FilledButton(
                    onPressed: () => context.go(AppRoutes.bookAppointment),
                    child: const Text('Reservar cita'),
                  ),
                ],
              ),
            ),
          );
        }

        final now = DateTime.now();
        final upcoming =
            appointments.where((a) => a.isUpcoming(now)).toList();
        final past =
            appointments.where((a) => !a.isUpcoming(now)).toList();

        return RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(myAppointmentsProvider);
            await ref.read(myAppointmentsProvider.future);
          },
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              if (upcoming.isNotEmpty) ...[
                const _SectionHeader(title: 'Próximas'),
                ...upcoming.map(
                  (appointment) => Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: AppointmentTile(
                      appointment: appointment,
                      isUpcoming: true,
                    ),
                  ),
                ),
              ],
              if (past.isNotEmpty) ...[
                if (upcoming.isNotEmpty) const SizedBox(height: 8),
                const _SectionHeader(title: 'Pasadas'),
                ...past.map(
                  (appointment) => Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: AppointmentTile(
                      appointment: appointment,
                      isUpcoming: false,
                    ),
                  ),
                ),
              ],
            ],
          ),
        );
      },
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Text(
        title,
        style: theme.textTheme.titleSmall?.copyWith(
          color: theme.colorScheme.primary,
          fontWeight: FontWeight.bold,
          letterSpacing: 0.5,
        ),
      ),
    );
  }
}
