import 'package:barberia_app/app/providers/app_state_providers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AppStateNotifier', () {
    test('inicia con valores base', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final state = container.read(appStateProvider);

      expect(state.themeMode, ThemeMode.system);
      expect(state.locale.languageCode, 'es');
      expect(state.isInitialized, isFalse);
      expect(state.isGlobalLoading, isFalse);
    });

    test('actualiza theme y locale', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final notifier = container.read(appStateProvider.notifier);
      notifier.setThemeMode(ThemeMode.dark);
      notifier.setLocale(const Locale('en'));

      final state = container.read(appStateProvider);
      expect(state.themeMode, ThemeMode.dark);
      expect(state.locale.languageCode, 'en');
    });

    test('actualiza flags globales', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final notifier = container.read(appStateProvider.notifier);
      notifier.setInitialized(true);
      notifier.setGlobalLoading(true);

      expect(container.read(appInitializedProvider), isTrue);
      expect(container.read(globalLoadingProvider), isTrue);
    });
  });
}
