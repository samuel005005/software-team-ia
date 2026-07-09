import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/admin_client.dart';
import '../../domain/usecases/admin_clients_use_cases.dart';
import '../providers/admin_clients_providers.dart';
import '../widgets/admin_client_appointments_dialog.dart';

class AdminUsersPage extends ConsumerWidget {
  const AdminUsersPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final clientsAsync = ref.watch(adminClientsProvider);

    return clientsAsync.when(
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
                onPressed: () => ref.invalidate(adminClientsProvider),
                child: const Text('Reintentar'),
              ),
            ],
          ),
        ),
      ),
      data: (clients) {
        if (clients.isEmpty) {
          return const Center(
            child: Padding(
              padding: EdgeInsets.all(24),
              child: Text('No hay clientes registrados.'),
            ),
          );
        }

        return ListView.separated(
          padding: const EdgeInsets.all(16),
          itemCount: clients.length,
          separatorBuilder: (_, __) => const SizedBox(height: 12),
          itemBuilder: (context, index) {
            final client = clients[index];
            return _AdminClientCard(
              client: client,
              onViewAppointments: () => _openAppointmentsDialog(context, client),
              onToggleActive: (value) => _toggleActive(ref, client, value),
            );
          },
        );
      },
    );
  }

  Future<void> _openAppointmentsDialog(
    BuildContext context,
    AdminClient client,
  ) async {
    await showDialog<void>(
      context: context,
      builder: (context) => AdminClientAppointmentsDialog(client: client),
    );
  }

  Future<void> _toggleActive(
    WidgetRef ref,
    AdminClient client,
    bool isActive,
  ) async {
    final result = await ref.read(updateAdminClientUseCaseProvider).call(
          UpdateAdminClientParams(
            userId: client.userId,
            isActive: isActive,
          ),
        );

    result.when(
      success: (_) => ref.invalidate(adminClientsProvider),
      error: (_) => ref.invalidate(adminClientsProvider),
    );
  }
}

class _AdminClientCard extends StatelessWidget {
  const _AdminClientCard({
    required this.client,
    required this.onViewAppointments,
    required this.onToggleActive,
  });

  final AdminClient client;
  final VoidCallback onViewAppointments;
  final ValueChanged<bool> onToggleActive;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    client.fullName,
                    style: theme.textTheme.titleMedium,
                  ),
                ),
                if (!client.isActive)
                  const Chip(
                    label: Text('Inactivo'),
                    visualDensity: VisualDensity.compact,
                  ),
                IconButton(
                  tooltip: 'Ver citas',
                  onPressed: onViewAppointments,
                  icon: const Icon(Icons.event_note_outlined),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(client.email),
            const SizedBox(height: 4),
            Text(client.phone),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Cuenta activa'),
              value: client.isActive,
              onChanged: onToggleActive,
            ),
          ],
        ),
      ),
    );
  }
}
