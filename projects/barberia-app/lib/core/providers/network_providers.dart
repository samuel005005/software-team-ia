import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../navigation/session_notifier.dart';
import '../network/api_client.dart';
import '../network/api_client_factory.dart';
import '../network/auth_token_store.dart';
import 'app_config_provider.dart';

/// Cierra sesión, limpia tokens y borra persistencia segura.
Future<void> signOutUser(Ref ref) async {
  await ref.read(sessionNotifierProvider.notifier).signOut();
}

/// Cliente HTTP con interceptores de auth y errores.
final apiClientProvider = Provider<ApiClient>((ref) {
  final config = ref.watch(appConfigProvider);
  final tokenStore = ref.read(authTokenStoreProvider.notifier);

  return ApiClientFactory.create(
    config: config,
    tokenProvider: tokenStore,
    onSessionExpired: () {
      signOutUser(ref);
    },
    onRefreshToken: () async {
      // Refresh real en T-031.
      return false;
    },
  );
});

/// Acceso directo a la instancia de [Dio].
final dioProvider = Provider<Dio>((ref) {
  return ref.watch(apiClientProvider).dio;
});
