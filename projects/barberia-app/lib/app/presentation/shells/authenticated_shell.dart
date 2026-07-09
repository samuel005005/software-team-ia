import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/navigation/session_notifier.dart';
import '../../../core/navigation/user_role.dart';
import '../../../shared/widgets/feature_placeholder_page.dart';
import '../../router/routes.dart';

/// Shell con navegación inferior según rol autenticado.
class AuthenticatedShell extends ConsumerWidget {
  const AuthenticatedShell({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final session = ref.watch(sessionNotifierProvider);
    final role = session.role ?? UserRole.client;
    final currentPath = GoRouterState.of(context).uri.path;
    final destinations = _destinationsFor(role);

    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex(destinations, currentPath),
        onDestinationSelected: (index) {
          context.go(destinations[index].route);
        },
        destinations: [
          for (final item in destinations)
            NavigationDestination(
              icon: Icon(item.icon),
              label: item.label,
            ),
        ],
      ),
      appBar: AppBar(
        title: Text('Barbería — ${role.label}'),
        actions: [
          IconButton(
            tooltip: 'Cerrar sesión',
            onPressed: () async {
              await ref.read(sessionNotifierProvider.notifier).signOut();
              if (context.mounted) {
                context.go(AppRoutes.login);
              }
            },
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
    );
  }

  int _selectedIndex(List<_NavItem> items, String path) {
    final index = items.indexWhere((item) => item.route == path);
    return index >= 0 ? index : 0;
  }

  List<_NavItem> _destinationsFor(UserRole role) {
    switch (role) {
      case UserRole.client:
        return const [
          _NavItem(AppRoutes.home, 'Inicio', Icons.home_outlined),
          _NavItem(AppRoutes.services, 'Servicios', Icons.content_cut),
          _NavItem(AppRoutes.appointments, 'Citas', Icons.calendar_month),
          _NavItem(AppRoutes.profile, 'Perfil', Icons.person_outline),
        ];
      case UserRole.barber:
        return const [
          _NavItem(AppRoutes.barberSchedule, 'Agenda', Icons.schedule),
          _NavItem(
            AppRoutes.barberAvailability,
            'Disponibilidad',
            Icons.event_available,
          ),
          _NavItem(AppRoutes.profile, 'Perfil', Icons.person_outline),
        ];
      case UserRole.admin:
        return const [
          _NavItem(AppRoutes.adminDashboard, 'Panel', Icons.dashboard),
          _NavItem(AppRoutes.adminServices, 'Servicios', Icons.content_cut),
          _NavItem(AppRoutes.adminBarbers, 'Barberos', Icons.badge_outlined),
          _NavItem(AppRoutes.adminUsers, 'Usuarios', Icons.people_outline),
          _NavItem(
            AppRoutes.adminBusinessHours,
            'Horarios',
            Icons.access_time,
          ),
          _NavItem(AppRoutes.profile, 'Perfil', Icons.person_outline),
        ];
    }
  }
}

final class _NavItem {
  const _NavItem(this.route, this.label, this.icon);

  final String route;
  final String label;
  final IconData icon;
}

/// Atajo para páginas placeholder dentro del shell autenticado.
Widget shellPlaceholder(String title, String module) {
  return FeaturePlaceholderPage(title: title, module: module);
}
