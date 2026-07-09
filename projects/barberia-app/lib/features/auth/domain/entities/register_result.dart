/// Resultado de registro exitoso (US-001).
class RegisterResult {
  const RegisterResult({
    required this.id,
    required this.email,
    required this.fullName,
    required this.message,
  });

  final String id;
  final String email;
  final String fullName;
  final String message;
}
