import 'package:barberia_app/app/app.dart';
import 'package:barberia_app/core/error/failures.dart';
import 'package:barberia_app/core/navigation/session_notifier.dart';
import 'package:barberia_app/core/navigation/user_role.dart';
import 'package:barberia_app/core/network/contracts/auth_token_provider.dart';
import 'package:barberia_app/core/providers/storage_providers.dart';
import 'package:barberia_app/core/storage/in_memory_secure_storage_service.dart';
import 'package:barberia_app/core/utils/result.dart';
import 'package:barberia_app/features/auth/domain/entities/login_result.dart';
import 'package:barberia_app/features/auth/domain/entities/register_result.dart';
import 'package:barberia_app/features/auth/domain/repositories/auth_repository.dart';
import 'package:barberia_app/features/auth/presentation/providers/auth_providers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeAuthRepository implements AuthRepository {
  @override
  Future<Result<LoginResult>> login({
    required String email,
    required String password,
  }) async {
    return const Success(
      LoginResult(
        tokens: AuthTokens(
          accessToken: 'mock-access-client',
          refreshToken: 'mock-refresh-client',
        ),
        role: UserRole.client,
      ),
    );
  }

  @override
  Future<Result<AuthTokens>> refresh({required String refreshToken}) async {
    return const Error(UnknownFailure('not used'));
  }

  @override
  Future<Result<RegisterResult>> register({
    required String email,
    required String password,
    required String fullName,
    required String phone,
  }) async {
    return const Error(UnknownFailure('not used'));
  }
}

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
        authRepositoryProvider.overrideWithValue(_FakeAuthRepository()),
      ],
      child: const BarberiaApp(),
    );
  }

  testWidgets('BarberiaApp redirige a login sin sesión', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    expect(find.text('Accede con tu cuenta'), findsOneWidget);
  });

  testWidgets('login como cliente navega al inicio', (tester) async {
    await tester.pumpWidget(buildApp());
    await tester.pumpAndSettle();

    await tester.tap(find.text('Mock: Cliente'));
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
        authRepositoryProvider.overrideWithValue(_FakeAuthRepository()),
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

    expect(find.text('Accede con tu cuenta'), findsOneWidget);
  });
}
