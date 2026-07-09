import '../../core/navigation/auth_session.dart';
import '../../core/navigation/user_role.dart';
import 'routes.dart';

/// Lógica pura de redirección para GoRouter (testeable sin widgets).
abstract final class RouterRedirect {
  static String? resolve({
    required AuthSession session,
    required String matchedLocation,
  }) {
    final location = _normalize(matchedLocation);

    if (location == AppRoutes.root) {
      return session.isAuthenticated ? session.homeRoute : AppRoutes.login;
    }

    if (!session.isAuthenticated) {
      return AppRoutes.isPublic(location) ? null : AppRoutes.login;
    }

    if (AppRoutes.isPublic(location)) {
      return session.homeRoute;
    }

    final role = session.role;
    if (role == null) return AppRoutes.login;

    if (!canAccess(role, location)) {
      return session.homeRoute;
    }

    return null;
  }

  static bool canAccess(UserRole role, String location) {
    if (AppRoutes.isShared(location)) return true;
    if (AppRoutes.isClientOnly(location)) return role == UserRole.client;
    if (AppRoutes.isBarberArea(location)) return role == UserRole.barber;
    if (AppRoutes.isAdminArea(location)) return role == UserRole.admin;
    return false;
  }

  static String _normalize(String location) {
    final uri = Uri.tryParse(location);
    if (uri == null) return location;
    return uri.hasEmptyPath ? AppRoutes.root : uri.path;
  }
}
