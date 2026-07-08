import '../navigation/user_role.dart';
import '../network/contracts/auth_token_provider.dart';
import 'secure_storage_service.dart';
import 'storage_keys.dart';

/// Snapshot persistido de sesión autenticada.
class PersistedSession {
  const PersistedSession({
    required this.tokens,
    required this.role,
  });

  final AuthTokens tokens;
  final UserRole role;
}

/// Persistencia segura de tokens y rol de usuario.
class SessionPersistence {
  SessionPersistence(this._storage);

  final SecureStorageService _storage;

  Future<void> save({
    required AuthTokens tokens,
    required UserRole role,
  }) async {
    await Future.wait([
      _storage.write(StorageKeys.accessToken, tokens.accessToken),
      _storage.write(StorageKeys.refreshToken, tokens.refreshToken),
      _storage.write(StorageKeys.userRole, role.name),
    ]);
  }

  Future<PersistedSession?> load() async {
    final accessToken = await _storage.read(StorageKeys.accessToken);
    final refreshToken = await _storage.read(StorageKeys.refreshToken);
    final roleName = await _storage.read(StorageKeys.userRole);

    if (accessToken == null ||
        refreshToken == null ||
        roleName == null ||
        accessToken.isEmpty ||
        refreshToken.isEmpty) {
      return null;
    }

    final role = _parseRole(roleName);
    if (role == null) return null;

    return PersistedSession(
      tokens: AuthTokens(
        accessToken: accessToken,
        refreshToken: refreshToken,
      ),
      role: role,
    );
  }

  Future<void> clear() async {
    await Future.wait([
      _storage.delete(StorageKeys.accessToken),
      _storage.delete(StorageKeys.refreshToken),
      _storage.delete(StorageKeys.userRole),
    ]);
  }

  UserRole? _parseRole(String value) {
    for (final role in UserRole.values) {
      if (role.name == value) return role;
    }
    return null;
  }
}
