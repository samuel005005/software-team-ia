import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/navigation/user_role.dart';
import '../../../../app/providers/app_state_providers.dart';
import '../../../../app/router/routes.dart';
import '../../../../core/navigation/session_notifier.dart';
import '../../../../core/network/contracts/auth_token_provider.dart';
import '../../domain/usecases/login_use_case.dart';
import '../providers/auth_providers.dart';

class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});

  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isLoading = ref.watch(globalLoadingProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Iniciar sesión')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Accede con tu cuenta',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 24),
              TextFormField(
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                autofillHints: const [AutofillHints.email],
                decoration: const InputDecoration(
                  labelText: 'Email',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Ingresa tu email';
                  }
                  if (!value.contains('@')) {
                    return 'Email inválido';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _passwordController,
                obscureText: true,
                autofillHints: const [AutofillHints.password],
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
              const SizedBox(height: 24),
              FilledButton(
                onPressed: isLoading ? null : _submitLogin,
                child: const Text('Iniciar sesión'),
              ),
              if (isLoading) ...[
                const SizedBox(height: 12),
                const LinearProgressIndicator(),
              ],
              const SizedBox(height: 16),
              OutlinedButton(
                onPressed: isLoading
                    ? null
                    : () => context.go(AppRoutes.register),
                child: const Text('Crear cuenta'),
              ),
              if (kDebugMode) ...[
                const SizedBox(height: 32),
                const Divider(),
                Text(
                  'Acceso rápido (solo desarrollo)',
                  style: Theme.of(context).textTheme.labelLarge,
                ),
                const SizedBox(height: 12),
                OutlinedButton(
                  onPressed: isLoading ? null : () => _mockSignIn(UserRole.client),
                  child: const Text('Mock: Cliente'),
                ),
                const SizedBox(height: 8),
                OutlinedButton(
                  onPressed: isLoading ? null : () => _mockSignIn(UserRole.barber),
                  child: const Text('Mock: Barbero'),
                ),
                const SizedBox(height: 8),
                OutlinedButton(
                  onPressed: isLoading ? null : () => _mockSignIn(UserRole.admin),
                  child: const Text('Mock: Admin'),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _submitLogin() async {
    if (!_formKey.currentState!.validate()) return;

    ref.read(appStateProvider.notifier).setGlobalLoading(true);
    final result = await ref.read(loginUseCaseProvider).call(
          LoginParams(
            email: _emailController.text,
            password: _passwordController.text,
          ),
        );
    ref.read(appStateProvider.notifier).setGlobalLoading(false);

    if (!mounted) return;

    result.when(
      success: (loginResult) async {
        await ref.read(sessionNotifierProvider.notifier).signInAs(
              loginResult.role,
              tokens: loginResult.tokens,
            );
        if (mounted) context.go(AppRoutes.root);
      },
      error: (failure) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(failure.message)),
        );
      },
    );
  }

  Future<void> _mockSignIn(UserRole role) async {
    ref.read(appStateProvider.notifier).setGlobalLoading(true);
    await ref.read(sessionNotifierProvider.notifier).signInAs(
          role,
          tokens: AuthTokens(
            accessToken: 'mock-access-${role.name}',
            refreshToken: 'mock-refresh-${role.name}',
          ),
        );
    ref.read(appStateProvider.notifier).setGlobalLoading(false);
    if (mounted) context.go(AppRoutes.root);
  }
}
