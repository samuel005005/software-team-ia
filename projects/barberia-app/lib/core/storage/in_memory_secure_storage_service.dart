import 'secure_storage_service.dart';

/// Implementación en memoria para tests.
class InMemorySecureStorageService implements SecureStorageService {
  final Map<String, String> _store = {};

  @override
  Future<void> delete(String key) async {
    _store.remove(key);
  }

  @override
  Future<void> deleteAll() async {
    _store.clear();
  }

  @override
  Future<String?> read(String key) async => _store[key];

  @override
  Future<void> write(String key, String value) async {
    _store[key] = value;
  }
}
