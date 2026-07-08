import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'contracts/auth_token_provider.dart';

/// Almacén en memoria de tokens JWT.
///
/// La persistencia segura se orquesta desde [SessionNotifier].
class AuthTokenStore extends Notifier<AuthTokens?> implements AuthTokenProvider {
  @override
  AuthTokens? build() => null;

  @override
  String? get accessToken => state?.accessToken;

  @override
  String? get refreshToken => state?.refreshToken;

  void restore(AuthTokens tokens) {
    state = tokens;
  }

  @override
  void setTokens(AuthTokens tokens) {
    state = tokens;
  }

  @override
  void clear() {
    state = null;
  }
}

final authTokenStoreProvider =
    NotifierProvider<AuthTokenStore, AuthTokens?>(AuthTokenStore.new);
