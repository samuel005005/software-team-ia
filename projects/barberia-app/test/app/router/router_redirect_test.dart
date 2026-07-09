import 'package:barberia_app/app/router/router_redirect.dart';
import 'package:barberia_app/app/router/routes.dart';
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

    test('cliente no accede a rutas de admin', () {
      final redirect = RouterRedirect.resolve(
        session: AuthSession.authenticated(role: UserRole.client),
        matchedLocation: '/admin/dashboard',
      );

      expect(redirect, '/home');
    });

    test('barbero no accede a rutas de cliente', () {
      final redirect = RouterRedirect.resolve(
        session: AuthSession.authenticated(role: UserRole.barber),
        matchedLocation: '/home',
      );

      expect(redirect, '/barber/schedule');
    });

    test('barbero no accede a rutas de admin', () {
      final redirect = RouterRedirect.resolve(
        session: AuthSession.authenticated(role: UserRole.barber),
        matchedLocation: '/admin/users',
      );

      expect(redirect, '/barber/schedule');
    });

    test('admin no accede a rutas de cliente', () {
      final redirect = RouterRedirect.resolve(
        session: AuthSession.authenticated(role: UserRole.admin),
        matchedLocation: '/appointments',
      );

      expect(redirect, '/admin/dashboard');
    });

    test('admin no accede a rutas de barbero', () {
      final redirect = RouterRedirect.resolve(
        session: AuthSession.authenticated(role: UserRole.admin),
        matchedLocation: '/barber/availability',
      );

      expect(redirect, '/admin/dashboard');
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

    test('todos los roles acceden a perfil', () {
      for (final role in UserRole.values) {
        expect(
          RouterRedirect.canAccess(role, AppRoutes.profile),
          isTrue,
          reason: role.name,
        );
      }
    });
  });
}
