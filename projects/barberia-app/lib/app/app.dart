import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'providers/app_providers.dart';
import 'theme/app_theme.dart';
import '../core/providers/core_providers.dart';

/// Widget raíz de la aplicación.
class BarberiaApp extends ConsumerWidget {
  const BarberiaApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final bootstrap = ref.watch(sessionBootstrapProvider);

    return bootstrap.when(
      loading: () => const MaterialApp(
        home: Scaffold(
          body: Center(child: CircularProgressIndicator()),
        ),
      ),
      error: (error, _) => MaterialApp(
        home: Scaffold(
          body: Center(child: Text('Error al iniciar: $error')),
        ),
      ),
      data: (_) => const _AppShell(),
    );
  }
}

class _AppShell extends ConsumerWidget {
  const _AppShell();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);
    final config = ref.watch(appConfigProvider);
    final themeMode = ref.watch(themeModeProvider);
    final locale = ref.watch(appLocaleProvider);

    return MaterialApp.router(
      title: config.appName,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: themeMode,
      locale: locale,
      routerConfig: router,
      debugShowCheckedModeBanner: config.isDevelopment,
    );
  }
}
