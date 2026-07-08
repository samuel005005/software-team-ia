import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../network/contracts/auth_token_provider.dart';
import '../network/auth_token_store.dart';
import '../providers/storage_providers.dart';
import 'auth_session.dart';
import 'user_role.dart';

/// Controlador de sesión de navegación con persistencia segura.
class SessionNotifier extends Notifier<AuthSession> {
  @override
  AuthSession build() => const AuthSession.unauthenticated();

  Future<void> signInAs(
    UserRole role, {
    required AuthTokens tokens,
  }) async {
    state = AuthSession.authenticated(role: role);
    ref.read(authTokenStoreProvider.notifier).setTokens(tokens);
    await ref.read(sessionPersistenceProvider).save(
          tokens: tokens,
          role: role,
        );
  }

  Future<void> signOut() async {
    state = const AuthSession.unauthenticated();
    ref.read(authTokenStoreProvider.notifier).clear();
    await ref.read(sessionPersistenceProvider).clear();
  }

  void restore(UserRole role) {
    state = AuthSession.authenticated(role: role);
  }
}

final sessionNotifierProvider =
    NotifierProvider<SessionNotifier, AuthSession>(SessionNotifier.new);
