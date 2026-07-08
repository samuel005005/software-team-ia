import 'package:barberia_app/core/network/auth_token_store.dart';
import 'package:barberia_app/core/network/contracts/auth_token_provider.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AuthTokenStore', () {
    test('guarda y limpia tokens', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final store = container.read(authTokenStoreProvider.notifier);
      store.setTokens(
        const AuthTokens(
          accessToken: 'access',
          refreshToken: 'refresh',
        ),
      );

      expect(container.read(authTokenStoreProvider)?.accessToken, 'access');
      expect(store.refreshToken, 'refresh');

      store.clear();
      expect(container.read(authTokenStoreProvider), isNull);
    });
  });
}
