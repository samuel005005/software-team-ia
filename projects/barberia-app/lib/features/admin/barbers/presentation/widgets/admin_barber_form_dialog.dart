import 'package:flutter/material.dart';

import '../../domain/entities/admin_barber.dart';

class AdminBarberFormDialog extends StatefulWidget {
  const AdminBarberFormDialog({
    super.key,
    this.barber,
  });

  final AdminBarber? barber;

  bool get isEditing => barber != null;

  @override
  State<AdminBarberFormDialog> createState() => _AdminBarberFormDialogState();
}

class _AdminBarberFormDialogState extends State<AdminBarberFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _emailController;
  late final TextEditingController _passwordController;
  late final TextEditingController _displayNameController;
  late final TextEditingController _bioController;
  late final TextEditingController _photoUrlController;
  late bool _isBookable;
  late bool _isActive;

  @override
  void initState() {
    super.initState();
    final barber = widget.barber;
    _emailController = TextEditingController(text: barber?.email ?? '');
    _passwordController = TextEditingController();
    _displayNameController = TextEditingController(text: barber?.displayName ?? '');
    _bioController = TextEditingController(text: barber?.bio ?? '');
    _photoUrlController = TextEditingController(text: barber?.photoUrl ?? '');
    _isBookable = barber?.isBookable ?? true;
    _isActive = barber?.isActive ?? true;
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _displayNameController.dispose();
    _bioController.dispose();
    _photoUrlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.isEditing ? 'Editar barbero' : 'Nuevo barbero'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _emailController,
                readOnly: widget.isEditing,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(
                  labelText: 'Email',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (widget.isEditing) return null;
                  if (value == null || !value.contains('@')) {
                    return 'Email inválido';
                  }
                  return null;
                },
              ),
              if (!widget.isEditing) ...[
                const SizedBox(height: 12),
                TextFormField(
                  controller: _passwordController,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'Contraseña',
                    border: OutlineInputBorder(),
                  ),
                  validator: (value) {
                    if (value == null || value.length < 8) {
                      return 'Mínimo 8 caracteres';
                    }
                    return null;
                  },
                ),
              ],
              const SizedBox(height: 12),
              TextFormField(
                controller: _displayNameController,
                decoration: const InputDecoration(
                  labelText: 'Nombre para mostrar',
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
                controller: _bioController,
                maxLines: 2,
                decoration: const InputDecoration(
                  labelText: 'Descripción (opcional)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _photoUrlController,
                decoration: const InputDecoration(
                  labelText: 'URL de foto (opcional)',
                  border: OutlineInputBorder(),
                ),
              ),
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Reservable'),
                value: _isBookable,
                onChanged: (value) => setState(() => _isBookable = value),
              ),
              if (widget.isEditing)
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
      AdminBarberFormResult(
        email: _emailController.text.trim(),
        password: _passwordController.text,
        displayName: _displayNameController.text.trim(),
        bio: _bioController.text.trim(),
        photoUrl: _photoUrlController.text.trim(),
        isBookable: _isBookable,
        isActive: _isActive,
      ),
    );
  }
}

class AdminBarberFormResult {
  const AdminBarberFormResult({
    required this.email,
    required this.password,
    required this.displayName,
    required this.bio,
    required this.photoUrl,
    required this.isBookable,
    required this.isActive,
  });

  final String email;
  final String password;
  final String displayName;
  final String bio;
  final String photoUrl;
  final bool isBookable;
  final bool isActive;
}
