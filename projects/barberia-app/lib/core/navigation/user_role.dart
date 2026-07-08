/// Roles de usuario definidos en SPEC.
enum UserRole {
  client,
  barber,
  admin,
}

extension UserRoleX on UserRole {
  String get label {
    switch (this) {
      case UserRole.client:
        return 'Cliente';
      case UserRole.barber:
        return 'Barbero';
      case UserRole.admin:
        return 'Administrador';
    }
  }
}
