import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../config/app_config.dart';

/// Configuración de entorno cargada al iniciar la app.
final appConfigProvider = Provider<AppConfig>(
  (ref) => AppConfig.fromEnvironment(),
);
