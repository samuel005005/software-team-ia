import 'dart:convert';

import '../navigation/user_role.dart';

/// Decodifica payload JWT (sin verificar firma — solo lectura de claims en cliente).
abstract final class JwtDecoder {
  static Map<String, dynamic>? decodePayload(String token) {
    final parts = token.split('.');
    if (parts.length != 3) return null;

    try {
      final normalized = base64Url.normalize(parts[1]);
      final decoded = utf8.decode(base64Url.decode(normalized));
      final payload = jsonDecode(decoded);
      return payload is Map<String, dynamic> ? payload : null;
    } catch (_) {
      return null;
    }
  }

  static UserRole? extractRole(String accessToken) {
    final role = decodePayload(accessToken)?['role'];
    if (role is! String) return null;

    return switch (role) {
      'client' => UserRole.client,
      'barber' => UserRole.barber,
      'admin' => UserRole.admin,
      _ => null,
    };
  }
}
