import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/navigation/session_notifier.dart';

/// Notifica a GoRouter cuando cambia la sesión.
class RouterRefreshNotifier extends ChangeNotifier {
  RouterRefreshNotifier(this._ref) {
    _ref.listen(sessionNotifierProvider, (previous, next) => notifyListeners());
  }

  final Ref _ref;
}

final routerRefreshNotifierProvider = Provider<RouterRefreshNotifier>((ref) {
  final notifier = RouterRefreshNotifier(ref);
  ref.onDispose(notifier.dispose);
  return notifier;
});
