import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../../app/providers/app_state_providers.dart';
import '../../domain/entities/admin_service.dart';
import '../../domain/usecases/admin_services_use_cases.dart';
import '../providers/admin_services_providers.dart';
import '../widgets/admin_service_form_dialog.dart';

class AdminServicesPage extends ConsumerWidget {
  const AdminServicesPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final servicesAsync = ref.watch(adminServicesProvider);

    return Stack(
      children: [
        servicesAsync.when(
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
                  onPressed: () => ref.invalidate(adminServicesProvider),
                  child: const Text('Reintentar'),
                ),
              ],
            ),
          ),
        ),
        data: (services) {
          if (services.isEmpty) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: Text('No hay servicios configurados. Crea el primero.'),
              ),
            );
          }

          return ListView.separated(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 88),
            itemCount: services.length,
            separatorBuilder: (_, __) => const SizedBox(height: 12),
            itemBuilder: (context, index) {
              final service = services[index];
              return _AdminServiceCard(
                service: service,
                onEdit: () => _openEditDialog(context, ref, service),
                onToggleActive: (value) => _toggleActive(ref, service, value),
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
    final result = await showDialog<AdminServiceFormResult>(
      context: context,
      builder: (context) => const AdminServiceFormDialog(),
    );
    if (result == null || !context.mounted) return;

    ref.read(appStateProvider.notifier).setGlobalLoading(true);
    final createResult = await ref.read(createAdminServiceUseCaseProvider).call(
          CreateAdminServiceParams(
            name: result.name,
            durationMinutes: result.durationMinutes,
            priceDop: result.priceDop,
            description: result.description.isEmpty ? null : result.description,
            isActive: result.isActive,
          ),
        );
    ref.read(appStateProvider.notifier).setGlobalLoading(false);

    if (!context.mounted) return;
    createResult.when(
      success: (_) {
        ref.invalidate(adminServicesProvider);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Servicio creado')),
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
    AdminService service,
  ) async {
    final result = await showDialog<AdminServiceFormResult>(
      context: context,
      builder: (context) => AdminServiceFormDialog(service: service),
    );
    if (result == null || !context.mounted) return;

    ref.read(appStateProvider.notifier).setGlobalLoading(true);
    final updateResult = await ref.read(updateAdminServiceUseCaseProvider).call(
          UpdateAdminServiceParams(
            id: service.id,
            name: result.name,
            durationMinutes: result.durationMinutes,
            priceDop: result.priceDop,
            description: result.description.isEmpty ? '' : result.description,
            isActive: result.isActive,
          ),
        );
    ref.read(appStateProvider.notifier).setGlobalLoading(false);

    if (!context.mounted) return;
    updateResult.when(
      success: (_) {
        ref.invalidate(adminServicesProvider);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Servicio actualizado')),
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
    AdminService service,
    bool isActive,
  ) async {
    final result = await ref.read(updateAdminServiceUseCaseProvider).call(
          UpdateAdminServiceParams(
            id: service.id,
            isActive: isActive,
          ),
        );

    result.when(
      success: (_) => ref.invalidate(adminServicesProvider),
      error: (failure) {
        ref.invalidate(adminServicesProvider);
      },
    );
  }
}

class _AdminServiceCard extends StatelessWidget {
  const _AdminServiceCard({
    required this.service,
    required this.onEdit,
    required this.onToggleActive,
  });

  final AdminService service;
  final VoidCallback onEdit;
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
                    service.name,
                    style: theme.textTheme.titleMedium,
                  ),
                ),
                if (!service.isActive)
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
            if (service.description != null && service.description!.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(service.description!),
            ],
            const SizedBox(height: 12),
            Row(
              children: [
                Text('${service.durationMinutes} min'),
                const Spacer(),
                Text('RD\$${service.priceDop}'),
              ],
            ),
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Disponible para reservas'),
              value: service.isActive,
              onChanged: onToggleActive,
            ),
          ],
        ),
      ),
    );
  }
}
