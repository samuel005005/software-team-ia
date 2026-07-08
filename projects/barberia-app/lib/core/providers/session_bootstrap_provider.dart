import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/providers/app_state_providers.dart';
import '../navigation/session_notifier.dart';
import '../network/auth_token_store.dart';
import 'storage_providers.dart';

/// Restaura sesión persistida al iniciar la app.
final sessionBootstrapProvider = FutureProvider<void>((ref) async {
  final persisted = await ref.read(sessionPersistenceProvider).load();

  if (persisted != null) {
    ref.read(authTokenStoreProvider.notifier).restore(persisted.tokens);
    ref.read(sessionNotifierProvider.notifier).restore(persisted.role);
  }

  ref.read(appStateProvider.notifier).setInitialized(true);
});
