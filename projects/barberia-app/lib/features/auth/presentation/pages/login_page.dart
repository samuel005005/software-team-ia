import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/navigation/session_notifier.dart';
import '../../../../core/navigation/user_role.dart';
import '../../../../core/network/contracts/auth_token_provider.dart';
import '../../../../app/router/routes.dart';
import '../../../../app/providers/app_state_providers.dart';

/// Pantalla pública de login (sin API — solo navegación T-002).
class LoginPage extends ConsumerWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isLoading = ref.watch(globalLoadingProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Iniciar sesión')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Acceso temporal para probar navegación',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            const Text(
              'La autenticación real se implementará en Fase 3 (T-030+).',
            ),
            const SizedBox(height: 24),
            FilledButton(
              onPressed: isLoading
                  ? null
                  : () => _signIn(ref, context, UserRole.client),
              child: const Text('Entrar como Cliente'),
            ),
            const SizedBox(height: 12),
            FilledButton(
              onPressed: isLoading
                  ? null
                  : () => _signIn(ref, context, UserRole.barber),
              child: const Text('Entrar como Barbero'),
            ),
            const SizedBox(height: 12),
            FilledButton(
              onPressed: isLoading
                  ? null
                  : () => _signIn(ref, context, UserRole.admin),
              child: const Text('Entrar como Administrador'),
            ),
            const SizedBox(height: 12),
            if (isLoading) const LinearProgressIndicator(),
            const SizedBox(height: 24),
            OutlinedButton(
              onPressed: () => context.go(AppRoutes.register),
              child: const Text('Ir a registro'),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              children: [
                OutlinedButton(
                  onPressed: () => ref
                      .read(appStateProvider.notifier)
                      .setThemeMode(ThemeMode.light),
                  child: const Text('Tema claro'),
                ),
                OutlinedButton(
                  onPressed: () => ref
                      .read(appStateProvider.notifier)
                      .setThemeMode(ThemeMode.dark),
                  child: const Text('Tema oscuro'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _signIn(
    WidgetRef ref,
    BuildContext context,
    UserRole role,
  ) async {
    ref.read(appStateProvider.notifier).setGlobalLoading(true);
    await ref.read(sessionNotifierProvider.notifier).signInAs(
          role,
          tokens: AuthTokens(
            accessToken: 'mock-access-${role.name}',
            refreshToken: 'mock-refresh-${role.name}',
          ),
        );
    ref.read(appStateProvider.notifier).setGlobalLoading(false);
    if (context.mounted) {
      context.go(AppRoutes.root);
    }
  }
}
