import 'user_role.dart';

/// Estado de sesión usado por el router.
class AuthSession {
  const AuthSession({
    required this.isAuthenticated,
    this.role,
  });

  final bool isAuthenticated;
  final UserRole? role;

  const AuthSession.unauthenticated()
      : isAuthenticated = false,
        role = null;

  AuthSession.authenticated({required UserRole this.role})
      : isAuthenticated = true;

  String get homeRoute {
    switch (role) {
      case UserRole.barber:
        return '/barber/schedule';
      case UserRole.admin:
        return '/admin/dashboard';
      case UserRole.client:
      case null:
        return '/home';
    }
  }
}
