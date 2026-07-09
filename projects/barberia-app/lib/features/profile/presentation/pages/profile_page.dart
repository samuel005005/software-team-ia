import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../app/providers/app_state_providers.dart';
import '../../../../core/navigation/user_role.dart';
import '../../domain/entities/user_profile.dart';
import '../../domain/usecases/profile_use_cases.dart';
import '../providers/profile_providers.dart';

class ProfilePage extends ConsumerWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(myProfileProvider);

    return profileAsync.when(
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
                onPressed: () => ref.invalidate(myProfileProvider),
                child: const Text('Reintentar'),
              ),
            ],
          ),
        ),
      ),
      data: (profile) {
        return switch (profile.role) {
          UserRole.client => const ClientProfilePage(),
          UserRole.barber => const BarberProfilePage(),
          UserRole.admin => const Center(
              child: Padding(
                padding: EdgeInsets.all(24),
                child: Text(
                  'El perfil editable para administradores no está disponible en MVP.',
                  textAlign: TextAlign.center,
                ),
              ),
            ),
        };
      },
    );
  }
}

class ClientProfilePage extends ConsumerStatefulWidget {
  const ClientProfilePage({super.key});

  @override
  ConsumerState<ClientProfilePage> createState() => _ClientProfilePageState();
}

class _ClientProfilePageState extends ConsumerState<ClientProfilePage> {
  final _formKey = GlobalKey<FormState>();
  final _fullNameController = TextEditingController();
  final _phoneController = TextEditingController();
  String? _email;
  bool _initialized = false;

  @override
  void dispose() {
    _fullNameController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  void _initializeFields(UserProfile profile) {
    if (_initialized) return;
    _fullNameController.text = profile.fullName;
    _phoneController.text = profile.phone ?? '';
    _email = profile.email;
    _initialized = true;
  }

  @override
  Widget build(BuildContext context) {
    final profileAsync = ref.watch(myProfileProvider);
    final isLoading = ref.watch(globalLoadingProvider);

    return profileAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => Center(child: Text(error.toString())),
      data: (profile) {
        _initializeFields(profile);

        return SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Mi perfil',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 24),
                TextFormField(
                  initialValue: _email,
                  readOnly: true,
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    border: OutlineInputBorder(),
                    helperText: 'No editable en MVP',
                  ),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _fullNameController,
                  textCapitalization: TextCapitalization.words,
                  decoration: const InputDecoration(
                    labelText: 'Nombre completo',
                    border: OutlineInputBorder(),
                  ),
                  validator: (value) {
                    if (value == null || value.trim().length < 2) {
                      return 'Ingresa tu nombre';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _phoneController,
                  keyboardType: TextInputType.phone,
                  decoration: const InputDecoration(
                    labelText: 'Teléfono',
                    border: OutlineInputBorder(),
                  ),
                  validator: (value) {
                    if (value == null || value.trim().length < 7) {
                      return 'Teléfono inválido';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 24),
                FilledButton(
                  onPressed: isLoading ? null : () => _saveProfile(context),
                  child: const Text('Guardar cambios'),
                ),
                if (isLoading) ...[
                  const SizedBox(height: 12),
                  const LinearProgressIndicator(),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  Future<void> _saveProfile(BuildContext context) async {
    if (!_formKey.currentState!.validate()) return;

    ref.read(appStateProvider.notifier).setGlobalLoading(true);
    final result = await ref.read(updateMyProfileUseCaseProvider).call(
          UpdateMyProfileParams(
            fullName: _fullNameController.text.trim(),
            phone: _phoneController.text.trim(),
          ),
        );
    ref.read(appStateProvider.notifier).setGlobalLoading(false);

    if (!context.mounted) return;

    result.when(
      success: (_) {
        ref.invalidate(myProfileProvider);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Perfil actualizado')),
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

class BarberProfilePage extends ConsumerStatefulWidget {
  const BarberProfilePage({super.key});

  @override
  ConsumerState<BarberProfilePage> createState() => _BarberProfilePageState();
}

class _BarberProfilePageState extends ConsumerState<BarberProfilePage> {
  final _formKey = GlobalKey<FormState>();
  final _displayNameController = TextEditingController();
  final _bioController = TextEditingController();
  final _photoUrlController = TextEditingController();
  String? _email;
  bool _initialized = false;

  @override
  void dispose() {
    _displayNameController.dispose();
    _bioController.dispose();
    _photoUrlController.dispose();
    super.dispose();
  }

  void _initializeFields(UserProfile profile) {
    if (_initialized) return;
    _displayNameController.text = profile.fullName;
    _bioController.text = profile.bio ?? '';
    _photoUrlController.text = profile.photoUrl ?? '';
    _email = profile.email;
    _initialized = true;
  }

  @override
  Widget build(BuildContext context) {
    final profileAsync = ref.watch(myProfileProvider);
    final isLoading = ref.watch(globalLoadingProvider);

    return profileAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => Center(child: Text(error.toString())),
      data: (profile) {
        _initializeFields(profile);

        return SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Mi perfil profesional',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                Text(
                  'Esta información será visible para los clientes al reservar.',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                const SizedBox(height: 24),
                TextFormField(
                  initialValue: _email,
                  readOnly: true,
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    border: OutlineInputBorder(),
                    helperText: 'No editable en MVP',
                  ),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _displayNameController,
                  textCapitalization: TextCapitalization.words,
                  decoration: const InputDecoration(
                    labelText: 'Nombre para mostrar',
                    border: OutlineInputBorder(),
                  ),
                  validator: (value) {
                    if (value == null || value.trim().length < 2) {
                      return 'Ingresa un nombre para mostrar';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _bioController,
                  maxLines: 4,
                  maxLength: 2000,
                  decoration: const InputDecoration(
                    labelText: 'Descripción breve',
                    border: OutlineInputBorder(),
                    alignLabelWithHint: true,
                  ),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _photoUrlController,
                  keyboardType: TextInputType.url,
                  decoration: const InputDecoration(
                    labelText: 'URL de foto',
                    border: OutlineInputBorder(),
                    helperText: 'Enlace a tu foto de perfil',
                  ),
                ),
                const SizedBox(height: 24),
                FilledButton(
                  onPressed: isLoading ? null : () => _saveProfile(context),
                  child: const Text('Guardar cambios'),
                ),
                if (isLoading) ...[
                  const SizedBox(height: 12),
                  const LinearProgressIndicator(),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  Future<void> _saveProfile(BuildContext context) async {
    if (!_formKey.currentState!.validate()) return;

    ref.read(appStateProvider.notifier).setGlobalLoading(true);
    final result = await ref.read(updateMyProfileUseCaseProvider).call(
          UpdateMyProfileParams(
            fullName: _displayNameController.text.trim(),
            bio: _bioController.text.trim(),
            photoUrl: _photoUrlController.text.trim(),
          ),
        );
    ref.read(appStateProvider.notifier).setGlobalLoading(false);

    if (!context.mounted) return;

    result.when(
      success: (_) {
        ref.invalidate(myProfileProvider);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Perfil actualizado')),
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
