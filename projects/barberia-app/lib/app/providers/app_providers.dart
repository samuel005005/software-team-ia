import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../router/app_router.dart';
export 'app_state_providers.dart';

/// Proveedor del router reactivo a cambios de sesión.
final appRouterProvider = Provider<GoRouter>((ref) {
  return createAppRouter(ref);
});
