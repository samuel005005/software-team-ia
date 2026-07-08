import 'package:barberia_app/core/navigation/user_role.dart';
import 'package:barberia_app/core/network/contracts/auth_token_provider.dart';
import 'package:barberia_app/core/storage/in_memory_secure_storage_service.dart';
import 'package:barberia_app/core/storage/session_persistence.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('SessionPersistence', () {
    late SessionPersistence persistence;

    setUp(() {
      persistence = SessionPersistence(InMemorySecureStorageService());
    });

    test('guarda y restaura sesión', () async {
      const tokens = AuthTokens(
        accessToken: 'access-123',
        refreshToken: 'refresh-456',
      );

      await persistence.save(tokens: tokens, role: UserRole.client);
      final loaded = await persistence.load();

      expect(loaded, isNotNull);
      expect(loaded!.tokens.accessToken, 'access-123');
      expect(loaded.tokens.refreshToken, 'refresh-456');
      expect(loaded.role, UserRole.client);
    });

    test('clear elimina la sesión persistida', () async {
      await persistence.save(
        tokens: const AuthTokens(
          accessToken: 'a',
          refreshToken: 'r',
        ),
        role: UserRole.admin,
      );

      await persistence.clear();
      final loaded = await persistence.load();

      expect(loaded, isNull);
    });

    test('retorna null si faltan datos', () async {
      final loaded = await persistence.load();
      expect(loaded, isNull);
    });
  });
}
