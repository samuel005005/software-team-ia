/// Entornos soportados por la aplicación.
enum AppEnvironment {
  dev,
  staging,
  production,
}

extension AppEnvironmentX on AppEnvironment {
  String get label {
    switch (this) {
      case AppEnvironment.dev:
        return 'development';
      case AppEnvironment.staging:
        return 'staging';
      case AppEnvironment.production:
        return 'production';
    }
  }

  static AppEnvironment fromString(String value) {
    switch (value.toLowerCase()) {
      case 'staging':
        return AppEnvironment.staging;
      case 'production':
      case 'prod':
        return AppEnvironment.production;
      case 'development':
      case 'dev':
      default:
        return AppEnvironment.dev;
    }
  }
}
