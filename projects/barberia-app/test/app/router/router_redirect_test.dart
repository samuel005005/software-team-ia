import 'package:barberia_app/app/router/router_redirect.dart';
import 'package:barberia_app/core/navigation/auth_session.dart';
import 'package:barberia_app/core/navigation/user_role.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('RouterRedirect', () {
    test('sin sesión redirige raíz a login', () {
      final redirect = RouterRedirect.resolve(
        session: const AuthSession.unauthenticated(),
        matchedLocation: '/',
      );

      expect(redirect, '/login');
    });

    test('sin sesión redirige ruta protegida a login', () {
      final redirect = RouterRedirect.resolve(
        session: const AuthSession.unauthenticated(),
        matchedLocation: '/home',
      );

      expect(redirect, '/login');
    });

    test('con sesión permite rutas públicas hacia home del rol', () {
      final redirect = RouterRedirect.resolve(
        session: AuthSession.authenticated(role: UserRole.client),
        matchedLocation: '/login',
      );

      expect(redirect, '/home');
    });

    test('cliente no accede a rutas de barbero', () {
      final redirect = RouterRedirect.resolve(
        session: AuthSession.authenticated(role: UserRole.client),
        matchedLocation: '/barber/schedule',
      );

      expect(redirect, '/home');
    });

    test('barbero redirige raíz a su agenda', () {
      final redirect = RouterRedirect.resolve(
        session: AuthSession.authenticated(role: UserRole.barber),
        matchedLocation: '/',
      );

      expect(redirect, '/barber/schedule');
    });

    test('admin redirige raíz a panel', () {
      final redirect = RouterRedirect.resolve(
        session: AuthSession.authenticated(role: UserRole.admin),
        matchedLocation: '/',
      );

      expect(redirect, '/admin/dashboard');
    });
  });
}
