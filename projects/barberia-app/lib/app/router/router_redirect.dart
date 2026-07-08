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

    if (AppRoutes.isBarberArea(location) && role != UserRole.barber) {
      return session.homeRoute;
    }

    if (AppRoutes.isAdminArea(location) && role != UserRole.admin) {
      return session.homeRoute;
    }

    if (_isClientOnlyRoute(location) &&
        role != UserRole.client &&
        !AppRoutes.barberRoutes.contains(location) &&
        !AppRoutes.adminRoutes.contains(location)) {
      return session.homeRoute;
    }

    return null;
  }

  static bool _isClientOnlyRoute(String location) =>
      AppRoutes.clientRoutes.contains(location);

  static String _normalize(String location) {
    final uri = Uri.tryParse(location);
    if (uri == null) return location;
    return uri.hasEmptyPath ? AppRoutes.root : uri.path;
  }
}
