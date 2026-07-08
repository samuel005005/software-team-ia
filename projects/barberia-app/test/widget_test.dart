import 'package:barberia_app/core/navigation/session_notifier.dart';
import 'package:barberia_app/core/navigation/user_role.dart';
import 'package:barberia_app/core/network/contracts/auth_token_provider.dart';
import 'package:barberia_app/core/providers/storage_providers.dart';
import 'package:barberia_app/core/storage/in_memory_secure_storage_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:barberia_app/app/app.dart';

void main() {
  Widget buildApp({ProviderContainer? container}) {
    if (container != null) {
      return UncontrolledProviderScope(
        container: container,
        child: const BarberiaApp(),
      );
    }

    return ProviderScope(
      overrides: [
        secureStorageServiceProvider.overrideWithValue(
          InMemorySecureStorageService(),
        ),
      ],
      child: const BarberiaApp(),
    );
  }

  testWidgets('BarberiaApp redirige a login sin sesión', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('Iniciar sesión'), findsOneWidget);
    expect(find.text('Entrar como Cliente'), findsOneWidget);
  });

  testWidgets('login como cliente navega al inicio', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    await tester.tap(find.text('Entrar como Cliente'));
    await tester.pumpAndSettle();

    expect(find.text('Inicio'), findsWidgets);
    expect(find.textContaining('client_booking'), findsOneWidget);
  });

  testWidgets('logout regresa a login', (tester) async {
    final container = ProviderContainer(
      overrides: [
        secureStorageServiceProvider.overrideWithValue(
          InMemorySecureStorageService(),
        ),
      ],
    );
    addTearDown(container.dispose);

    await container.read(sessionNotifierProvider.notifier).signInAs(
          UserRole.client,
          tokens: const AuthTokens(
            accessToken: 'access',
            refreshToken: 'refresh',
          ),
        );

    await tester.pumpWidget(buildApp(container: container));
    await tester.pumpAndSettle();

    await tester.tap(find.byTooltip('Cerrar sesión'));
    await tester.pumpAndSettle();

    expect(find.text('Iniciar sesión'), findsOneWidget);
  });
}
