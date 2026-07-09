import 'dart:convert';

import 'package:barberia_app/core/utils/jwt_decoder.dart';
import 'package:barberia_app/core/navigation/user_role.dart';
import 'package:flutter_test/flutter_test.dart';

String _fakeJwt(Map<String, dynamic> payload) {
  final header = base64Url.encode(utf8.encode('{"alg":"HS256"}'));
  final body = base64Url.encode(utf8.encode(jsonEncode(payload)));
  return '$header.$body.signature';
}

void main() {
  test('extractRole retorna client desde payload', () {
    final token = _fakeJwt({'role': 'client', 'sub': '123'});
    expect(JwtDecoder.extractRole(token), UserRole.client);
  });

  test('extractRole retorna null si falta role', () {
    final token = _fakeJwt({'sub': '123'});
    expect(JwtDecoder.extractRole(token), isNull);
  });
}
