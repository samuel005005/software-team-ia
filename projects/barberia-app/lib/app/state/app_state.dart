import 'package:flutter/material.dart';

/// Estado global de la aplicación (UI + bootstrap).
class AppState {
  const AppState({
    this.themeMode = ThemeMode.system,
    this.locale = const Locale('es'),
    this.isInitialized = false,
    this.isGlobalLoading = false,
  });

  final ThemeMode themeMode;
  final Locale locale;
  final bool isInitialized;
  final bool isGlobalLoading;

  AppState copyWith({
    ThemeMode? themeMode,
    Locale? locale,
    bool? isInitialized,
    bool? isGlobalLoading,
  }) {
    return AppState(
      themeMode: themeMode ?? this.themeMode,
      locale: locale ?? this.locale,
      isInitialized: isInitialized ?? this.isInitialized,
      isGlobalLoading: isGlobalLoading ?? this.isGlobalLoading,
    );
  }
}
