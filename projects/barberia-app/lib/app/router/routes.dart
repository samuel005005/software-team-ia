/// Rutas de la aplicación alineadas a `docs/ARCHITECTURE.md`.
abstract final class AppRoutes {
  static const root = '/';

  // Públicas
  static const login = '/login';
  static const register = '/register';

  // Cliente
  static const home = '/home';
  static const services = '/services';
  static const bookAppointment = '/book-appointment';
  static const appointments = '/appointments';
  static const profile = '/profile';

  // Barbero
  static const barberSchedule = '/barber/schedule';
  static const barberAvailability = '/barber/availability';

  // Administrador
  static const adminDashboard = '/admin/dashboard';
  static const adminServices = '/admin/services';
  static const adminBarbers = '/admin/barbers';
  static const adminUsers = '/admin/users';
  static const adminBusinessHours = '/admin/business-hours';

  static const publicRoutes = {login, register};

  static const clientRoutes = {
    home,
    services,
    bookAppointment,
    appointments,
    profile,
  };

  static const barberRoutes = {
    barberSchedule,
    barberAvailability,
    profile,
  };

  static const adminRoutes = {
    adminDashboard,
    adminServices,
    adminBarbers,
    adminUsers,
    adminBusinessHours,
    profile,
  };

  static bool isPublic(String location) => publicRoutes.contains(location);

  static bool isBarberArea(String location) =>
      location.startsWith('/barber');

  static bool isAdminArea(String location) => location.startsWith('/admin');
}
