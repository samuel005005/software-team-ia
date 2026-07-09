import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../../app/providers/app_state_providers.dart';
import '../../domain/entities/admin_barber.dart';
import '../../domain/usecases/admin_barbers_use_cases.dart';
import '../providers/admin_barbers_providers.dart';
import '../widgets/admin_barber_form_dialog.dart';
import '../widgets/admin_barber_services_dialog.dart';

class AdminBarbersPage extends ConsumerWidget {
  const AdminBarbersPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final barbersAsync = ref.watch(adminBarbersProvider);

    return Stack(
      children: [
        barbersAsync.when(
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
                    onPressed: () => ref.invalidate(adminBarbersProvider),
                    child: const Text('Reintentar'),
                  ),
                ],
              ),
            ),
          ),
          data: (barbers) {
            if (barbers.isEmpty) {
              return const Center(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Text('No hay barberos registrados. Crea el primero.'),
                ),
              );
            }

            return ListView.separated(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 88),
              itemCount: barbers.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final barber = barbers[index];
                return _AdminBarberCard(
                  barber: barber,
                  onEdit: () => _openEditDialog(context, ref, barber),
                  onAssignServices: () => _openServicesDialog(context, ref, barber),
                  onToggleActive: (value) => _toggleActive(ref, barber, value),
                  onToggleBookable: (value) => _toggleBookable(ref, barber, value),
                );
              },
            );
          },
        ),
        Positioned(
          right: 16,
          bottom: 16,
          child: FloatingActionButton.extended(
            onPressed: () => _openCreateDialog(context, ref),
            icon: const Icon(Icons.add),
            label: const Text('Nuevo'),
          ),
        ),
      ],
    );
  }

  Future<void> _openCreateDialog(BuildContext context, WidgetRef ref) async {
    final result = await showDialog<AdminBarberFormResult>(
      context: context,
      builder: (context) => const AdminBarberFormDialog(),
    );
    if (result == null || !context.mounted) return;

    ref.read(appStateProvider.notifier).setGlobalLoading(true);
    final createResult = await ref.read(createAdminBarberUseCaseProvider).call(
          CreateAdminBarberParams(
            email: result.email,
            password: result.password,
            displayName: result.displayName,
            bio: result.bio.isEmpty ? null : result.bio,
            photoUrl: result.photoUrl.isEmpty ? null : result.photoUrl,
            isBookable: result.isBookable,
          ),
        );
    ref.read(appStateProvider.notifier).setGlobalLoading(false);

    if (!context.mounted) return;
    createResult.when(
      success: (_) {
        ref.invalidate(adminBarbersProvider);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Barbero creado')),
        );
      },
      error: (failure) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(failure.message)),
        );
      },
    );
  }

  Future<void> _openServicesDialog(
    BuildContext context,
    WidgetRef ref,
    AdminBarber barber,
  ) async {
    final selectedIds = await showDialog<List<String>>(
      context: context,
      builder: (context) => AdminBarberServicesDialog(barber: barber),
    );
    if (selectedIds == null || !context.mounted) return;

    ref.read(appStateProvider.notifier).setGlobalLoading(true);
    final result = await ref.read(setBarberServicesUseCaseProvider).call(
          SetBarberServicesParams(
            userId: barber.userId,
            serviceIds: selectedIds,
          ),
        );
    ref.read(appStateProvider.notifier).setGlobalLoading(false);

    if (!context.mounted) return;
    result.when(
      success: (_) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Servicios asignados')),
        );
      },
      error: (failure) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(failure.message)),
        );
      },
    );
  }

  Future<void> _openEditDialog(
    BuildContext context,
    WidgetRef ref,
    AdminBarber barber,
  ) async {
    final result = await showDialog<AdminBarberFormResult>(
      context: context,
      builder: (context) => AdminBarberFormDialog(barber: barber),
    );
    if (result == null || !context.mounted) return;

    ref.read(appStateProvider.notifier).setGlobalLoading(true);
    final updateResult = await ref.read(updateAdminBarberUseCaseProvider).call(
          UpdateAdminBarberParams(
            userId: barber.userId,
            displayName: result.displayName,
            bio: result.bio.isEmpty ? '' : result.bio,
            photoUrl: result.photoUrl.isEmpty ? '' : result.photoUrl,
            isBookable: result.isBookable,
            isActive: result.isActive,
          ),
        );
    ref.read(appStateProvider.notifier).setGlobalLoading(false);

    if (!context.mounted) return;
    updateResult.when(
      success: (_) {
        ref.invalidate(adminBarbersProvider);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Barbero actualizado')),
        );
      },
      error: (failure) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(failure.message)),
        );
      },
    );
  }

  Future<void> _toggleActive(
    WidgetRef ref,
    AdminBarber barber,
    bool isActive,
  ) async {
    final result = await ref.read(updateAdminBarberUseCaseProvider).call(
          UpdateAdminBarberParams(
            userId: barber.userId,
            isActive: isActive,
          ),
        );
    result.when(
      success: (_) => ref.invalidate(adminBarbersProvider),
      error: (_) => ref.invalidate(adminBarbersProvider),
    );
  }

  Future<void> _toggleBookable(
    WidgetRef ref,
    AdminBarber barber,
    bool isBookable,
  ) async {
    final result = await ref.read(updateAdminBarberUseCaseProvider).call(
          UpdateAdminBarberParams(
            userId: barber.userId,
            isBookable: isBookable,
          ),
        );
    result.when(
      success: (_) => ref.invalidate(adminBarbersProvider),
      error: (_) => ref.invalidate(adminBarbersProvider),
    );
  }
}

class _AdminBarberCard extends StatelessWidget {
  const _AdminBarberCard({
    required this.barber,
    required this.onEdit,
    required this.onAssignServices,
    required this.onToggleActive,
    required this.onToggleBookable,
  });

  final AdminBarber barber;
  final VoidCallback onEdit;
  final VoidCallback onAssignServices;
  final ValueChanged<bool> onToggleActive;
  final ValueChanged<bool> onToggleBookable;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        barber.displayName,
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      Text(barber.email),
                    ],
                  ),
                ),
                if (!barber.isActive)
                  const Chip(
                    label: Text('Inactivo'),
                    visualDensity: VisualDensity.compact,
                  ),
                IconButton(
                  tooltip: 'Editar',
                  onPressed: onEdit,
                  icon: const Icon(Icons.edit_outlined),
                ),
              ],
            ),
            if (barber.bio != null && barber.bio!.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(barber.bio!),
            ],
            Align(
              alignment: Alignment.centerLeft,
              child: TextButton.icon(
                onPressed: onAssignServices,
                icon: const Icon(Icons.content_cut_outlined),
                label: const Text('Asignar servicios'),
              ),
            ),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Activo'),
              value: barber.isActive,
              onChanged: onToggleActive,
            ),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Reservable'),
              value: barber.isBookable,
              onChanged: onToggleBookable,
            ),
          ],
        ),
      ),
    );
  }
}
