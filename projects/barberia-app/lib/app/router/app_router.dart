import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/navigation/session_notifier.dart';
import '../../features/admin/business_hours/presentation/pages/admin_business_hours_page.dart';
import '../../features/barber_schedule/presentation/pages/barber_availability_page.dart';
import '../../features/admin/barbers/presentation/pages/admin_barbers_page.dart';
import '../../features/admin/services/presentation/pages/admin_services_page.dart';
import '../../features/admin/users/presentation/pages/admin_users_page.dart';
import '../../features/appointments/presentation/pages/appointments_page.dart';
import '../../features/auth/presentation/pages/login_page.dart';
import '../../features/auth/presentation/pages/register_page.dart';
import '../../features/profile/presentation/pages/profile_page.dart';
import '../../features/client_booking/presentation/pages/book_appointment_page.dart';
import '../../features/services/presentation/pages/services_page.dart';
import '../presentation/shells/authenticated_shell.dart';
import 'router_redirect.dart';
import 'router_refresh_notifier.dart';
import 'routes.dart';

/// Configuración central de navegación con GoRouter.
GoRouter createAppRouter(Ref ref) {
  final refreshNotifier = ref.read(routerRefreshNotifierProvider);

  return GoRouter(
    initialLocation: AppRoutes.root,
    debugLogDiagnostics: true,
    refreshListenable: refreshNotifier,
    redirect: (context, state) {
      final session = ref.read(sessionNotifierProvider);
      return RouterRedirect.resolve(
        session: session,
        matchedLocation: state.matchedLocation,
      );
    },
    routes: [
      GoRoute(
        path: AppRoutes.root,
        redirect: (context, state) {
          final session = ref.read(sessionNotifierProvider);
          return RouterRedirect.resolve(
            session: session,
            matchedLocation: state.matchedLocation,
          );
        },
      ),
      GoRoute(
        path: AppRoutes.login,
        name: 'login',
        builder: (context, state) => const LoginPage(),
      ),
      GoRoute(
        path: AppRoutes.register,
        name: 'register',
        builder: (context, state) => const RegisterPage(),
      ),
      ShellRoute(
        builder: (context, state, child) =>
            AuthenticatedShell(child: child),
        routes: [
          GoRoute(
            path: AppRoutes.home,
            name: 'home',
            builder: (context, state) =>
                shellPlaceholder('Inicio', 'client_booking'),
          ),
          GoRoute(
            path: AppRoutes.services,
            name: 'services',
            builder: (context, state) => const ServicesPage(),
          ),
          GoRoute(
            path: AppRoutes.bookAppointment,
            name: 'book-appointment',
            builder: (context, state) => BookAppointmentPage(
              initialServiceId: state.uri.queryParameters['serviceId'],
            ),
          ),
          GoRoute(
            path: AppRoutes.appointments,
            name: 'appointments',
            builder: (context, state) => const AppointmentsPage(),
          ),
          GoRoute(
            path: AppRoutes.profile,
            name: 'profile',
            builder: (context, state) => const ProfilePage(),
          ),
          GoRoute(
            path: AppRoutes.barberSchedule,
            name: 'barber-schedule',
            builder: (context, state) =>
                shellPlaceholder('Agenda', 'barber_schedule'),
          ),
          GoRoute(
            path: AppRoutes.barberAvailability,
            name: 'barber-availability',
            builder: (context, state) => const BarberAvailabilityPage(),
          ),
          GoRoute(
            path: AppRoutes.adminDashboard,
            name: 'admin-dashboard',
            builder: (context, state) =>
                shellPlaceholder('Panel admin', 'admin_management'),
          ),
          GoRoute(
            path: AppRoutes.adminServices,
            name: 'admin-services',
            builder: (context, state) => const AdminServicesPage(),
          ),
          GoRoute(
            path: AppRoutes.adminBarbers,
            name: 'admin-barbers',
            builder: (context, state) => const AdminBarbersPage(),
          ),
          GoRoute(
            path: AppRoutes.adminUsers,
            name: 'admin-users',
            builder: (context, state) => const AdminUsersPage(),
          ),
          GoRoute(
            path: AppRoutes.adminBusinessHours,
            name: 'admin-business-hours',
            builder: (context, state) => const AdminBusinessHoursPage(),
          ),
        ],
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      appBar: AppBar(title: const Text('Ruta no encontrada')),
      body: Center(
        child: Text(state.error?.toString() ?? 'Página no disponible'),
      ),
    ),
  );
}
