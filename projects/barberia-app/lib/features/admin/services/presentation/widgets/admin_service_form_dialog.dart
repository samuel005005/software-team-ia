import 'package:flutter/material.dart';

import '../../domain/entities/admin_service.dart';

class AdminServiceFormDialog extends StatefulWidget {
  const AdminServiceFormDialog({
    super.key,
    this.service,
  });

  final AdminService? service;

  bool get isEditing => service != null;

  @override
  State<AdminServiceFormDialog> createState() => _AdminServiceFormDialogState();
}

class _AdminServiceFormDialogState extends State<AdminServiceFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nameController;
  late final TextEditingController _descriptionController;
  late final TextEditingController _durationController;
  late final TextEditingController _priceController;
  late bool _isActive;

  @override
  void initState() {
    super.initState();
    final service = widget.service;
    _nameController = TextEditingController(text: service?.name ?? '');
    _descriptionController = TextEditingController(text: service?.description ?? '');
    _durationController = TextEditingController(
      text: service?.durationMinutes.toString() ?? '30',
    );
    _priceController = TextEditingController(text: service?.priceDop ?? '');
    _isActive = service?.isActive ?? true;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _durationController.dispose();
    _priceController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.isEditing ? 'Editar servicio' : 'Nuevo servicio'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Nombre',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.trim().length < 2) {
                    return 'Nombre requerido';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _descriptionController,
                maxLines: 2,
                decoration: const InputDecoration(
                  labelText: 'Descripción (opcional)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _durationController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Duración (minutos)',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  final parsed = int.tryParse(value ?? '');
                  if (parsed == null || parsed <= 0) {
                    return 'Duración inválida';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _priceController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(
                  labelText: 'Precio (DOP)',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  final parsed = double.tryParse(value ?? '');
                  if (parsed == null || parsed <= 0) {
                    return 'Precio inválido';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 8),
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Activo'),
                value: _isActive,
                onChanged: (value) => setState(() => _isActive = value),
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancelar'),
        ),
        FilledButton(
          onPressed: _submit,
          child: Text(widget.isEditing ? 'Guardar' : 'Crear'),
        ),
      ],
    );
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;

    Navigator.of(context).pop(
      AdminServiceFormResult(
        name: _nameController.text.trim(),
        description: _descriptionController.text.trim(),
        durationMinutes: int.parse(_durationController.text.trim()),
        priceDop: _priceController.text.trim(),
        isActive: _isActive,
      ),
    );
  }
}

class AdminServiceFormResult {
  const AdminServiceFormResult({
    required this.name,
    required this.description,
    required this.durationMinutes,
    required this.priceDop,
    required this.isActive,
  });

  final String name;
  final String description;
  final int durationMinutes;
  final String priceDop;
  final bool isActive;
}
