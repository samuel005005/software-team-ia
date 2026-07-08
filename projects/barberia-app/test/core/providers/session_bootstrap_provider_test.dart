import 'package:barberia_app/core/providers/session_bootstrap_provider.dart';
import 'package:barberia_app/core/providers/storage_providers.dart';
import 'package:barberia_app/core/storage/in_memory_secure_storage_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('sessionBootstrapProvider completa con storage en memoria', () async {
    final container = ProviderContainer(
      overrides: [
        secureStorageServiceProvider.overrideWithValue(
          InMemorySecureStorageService(),
        ),
      ],
    );
    addTearDown(container.dispose);

    await container.read(sessionBootstrapProvider.future);

    expect(container.read(sessionBootstrapProvider).hasValue, isTrue);
  });
}
