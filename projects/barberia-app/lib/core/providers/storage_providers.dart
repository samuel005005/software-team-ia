import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../storage/flutter_secure_storage_service.dart';
import '../storage/secure_storage_service.dart';
import '../storage/session_persistence.dart';

final secureStorageServiceProvider = Provider<SecureStorageService>(
  (ref) => FlutterSecureStorageService(),
);

final sessionPersistenceProvider = Provider<SessionPersistence>((ref) {
  return SessionPersistence(ref.watch(secureStorageServiceProvider));
});
