import 'environment.dart';

/// Configuración centralizada de la aplicación por entorno.
class AppConfig {
  const AppConfig({
    required this.environment,
    required this.appName,
    required this.apiBaseUrl,
    required this.enableLogging,
  });

  final AppEnvironment environment;
  final String appName;
  final String apiBaseUrl;
  final bool enableLogging;

  bool get isDevelopment => environment == AppEnvironment.dev;

  factory AppConfig.fromEnvironment() {
    const envName = String.fromEnvironment('APP_ENV', defaultValue: 'dev');
    final environment = AppEnvironmentX.fromString(envName);

    switch (environment) {
      case AppEnvironment.staging:
        return const AppConfig(
          environment: AppEnvironment.staging,
          appName: 'Barbería App',
          apiBaseUrl: 'https://staging-api.barberia-app.local/api/v1',
          enableLogging: true,
        );
      case AppEnvironment.production:
        return const AppConfig(
          environment: AppEnvironment.production,
          appName: 'Barbería App',
          apiBaseUrl: 'https://api.barberia-app.local/api/v1',
          enableLogging: false,
        );
      case AppEnvironment.dev:
        return const AppConfig(
          environment: AppEnvironment.dev,
          appName: 'Barbería App (Dev)',
          apiBaseUrl: 'http://localhost:8000/api/v1',
          enableLogging: true,
        );
    }
  }
}
