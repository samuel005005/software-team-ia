import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../services/domain/entities/service_item.dart';
import '../../../../services/presentation/providers/services_providers.dart';
import '../../domain/entities/admin_barber.dart';
import '../../domain/usecases/admin_barbers_use_cases.dart';
import '../providers/admin_barbers_providers.dart';

class AdminBarberServicesDialog extends ConsumerStatefulWidget {
  const AdminBarberServicesDialog({super.key, required this.barber});

  final AdminBarber barber;

  @override
  ConsumerState<AdminBarberServicesDialog> createState() =>
      _AdminBarberServicesDialogState();
}

class _AdminBarberServicesDialogState extends ConsumerState<AdminBarberServicesDialog> {
  final Set<String> _selectedIds = {};
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadAssigned();
  }

  Future<void> _loadAssigned() async {
    final result = await ref.read(getBarberServiceIdsUseCaseProvider).call(
          GetBarberServiceIdsParams(widget.barber.userId),
        );

    if (!mounted) return;

    result.when(
      success: (ids) {
        setState(() {
          _selectedIds
            ..clear()
            ..addAll(ids);
          _loading = false;
        });
      },
      error: (failure) {
        setState(() {
          _error = failure.message;
          _loading = false;
        });
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final servicesAsync = ref.watch(activeServicesProvider);

    return AlertDialog(
      title: Text('Servicios — ${widget.barber.displayName}'),
      content: SizedBox(
        width: double.maxFinite,
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : _error != null
                ? Text(_error!)
                : servicesAsync.when(
                    loading: () => const Center(child: CircularProgressIndicator()),
                    error: (error, _) => Text(error.toString()),
                    data: (services) => _buildServiceList(services),
                  ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancelar'),
        ),
        FilledButton(
          onPressed: _loading ? null : () => Navigator.of(context).pop(_selectedIds.toList()),
          child: const Text('Guardar'),
        ),
      ],
    );
  }

  Widget _buildServiceList(List<ServiceItem> services) {
    if (services.isEmpty) {
      return const Text('No hay servicios activos para asignar.');
    }

    return ListView.builder(
      shrinkWrap: true,
      itemCount: services.length,
      itemBuilder: (context, index) {
        final service = services[index];
        final selected = _selectedIds.contains(service.id);

        return CheckboxListTile(
          value: selected,
          onChanged: (value) {
            setState(() {
              if (value == true) {
                _selectedIds.add(service.id);
              } else {
                _selectedIds.remove(service.id);
              }
            });
          },
          title: Text(service.name),
          subtitle: Text('${service.durationMinutes} min · RD\$${service.priceDop}'),
        );
      },
    );
  }
}
