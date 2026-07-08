import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../state/app_state.dart';

/// Estado global base de la app para configuración UI.
class AppStateNotifier extends Notifier<AppState> {
  @override
  AppState build() => const AppState();

  void setThemeMode(ThemeMode mode) {
    state = state.copyWith(themeMode: mode);
  }

  void setLocale(Locale locale) {
    state = state.copyWith(locale: locale);
  }

  void setInitialized(bool value) {
    state = state.copyWith(isInitialized: value);
  }

  void setGlobalLoading(bool value) {
    state = state.copyWith(isGlobalLoading: value);
  }
}

final appStateProvider = NotifierProvider<AppStateNotifier, AppState>(
  AppStateNotifier.new,
);

final themeModeProvider = Provider<ThemeMode>((ref) {
  return ref.watch(appStateProvider).themeMode;
});

final appLocaleProvider = Provider<Locale>((ref) {
  return ref.watch(appStateProvider).locale;
});

final appInitializedProvider = Provider<bool>((ref) {
  return ref.watch(appStateProvider).isInitialized;
});

final globalLoadingProvider = Provider<bool>((ref) {
  return ref.watch(appStateProvider).isGlobalLoading;
});
