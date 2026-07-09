class EmailAlreadyExistsError(Exception):
    """El email ya está registrado en el sistema."""


class InvalidCredentialsError(Exception):
    """Email o contraseña incorrectos."""


class InactiveUserError(Exception):
    """La cuenta del usuario está desactivada."""


class InvalidRefreshTokenError(Exception):
    """Refresh token inválido, expirado o revocado."""


class ProfileNotFoundError(Exception):
    """Perfil de usuario no encontrado."""


class ProfileUpdateForbiddenError(Exception):
    """El rol no puede actualizar perfil por este endpoint."""
