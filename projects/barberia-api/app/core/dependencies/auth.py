import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.dependencies.database import get_db
from app.domain.enums import UserRole
from app.infrastructure.db.models.user import User
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.security.jwt_service import JwtService

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida",
        )

    jwt_service = JwtService()
    try:
        payload = jwt_service.decode_access_token(credentials.credentials)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        ) from exc

    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    user = UserRepository(db).get_by_id_with_profiles(uuid.UUID(str(subject)))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autorizado",
        )
    return user


def require_roles(*allowed: UserRole) -> Callable[..., User]:
    allowed_set = set(allowed)

    def _dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para esta operación",
            )
        return user

    return _dependency


def require_client(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo clientes pueden acceder a este recurso",
        )
    if user.client_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de cliente no encontrado",
        )
    return user


require_barber = require_roles(UserRole.BARBER)
require_admin = require_roles(UserRole.ADMIN)
require_authenticated = get_current_user
