from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.auth.errors import InactiveUserError, InvalidCredentialsError, InvalidRefreshTokenError
from app.domain.enums import UserRole
from app.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.security.jwt_service import JwtService, generate_refresh_token
from app.infrastructure.security.password_hasher import verify_password


@dataclass(frozen=True)
class LoginCommand:
    email: str
    password: str


@dataclass(frozen=True)
class RefreshSessionCommand:
    refresh_token: str


@dataclass(frozen=True)
class AuthTokensResult:
    access_token: str
    refresh_token: str


class AuthTokenIssuer:
    def __init__(self, session: Session, jwt_service: JwtService | None = None) -> None:
        self._refresh_tokens = RefreshTokenRepository(session)
        self._jwt = jwt_service or JwtService()

    def issue(self, user_id: UUID, email: str, role: UserRole) -> AuthTokensResult:
        access_token = self._jwt.create_access_token(user_id, email, role)
        plain_refresh, token_hash = generate_refresh_token()
        self._refresh_tokens.create(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=self._jwt.refresh_token_expires_at(),
        )
        return AuthTokensResult(access_token=access_token, refresh_token=plain_refresh)


class LoginUseCase:
    def __init__(self, session: Session, jwt_service: JwtService | None = None) -> None:
        self._users = UserRepository(session)
        self._issuer = AuthTokenIssuer(session, jwt_service)

    def execute(self, command: LoginCommand) -> AuthTokensResult:
        user = self._users.get_by_email(command.email)
        if user is None or not verify_password(command.password, user.password_hash):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        return self._issuer.issue(user.id, user.email, user.role)


class RefreshSessionUseCase:
    def __init__(self, session: Session, jwt_service: JwtService | None = None) -> None:
        self._users = UserRepository(session)
        self._refresh_tokens = RefreshTokenRepository(session)
        self._issuer = AuthTokenIssuer(session, jwt_service)

    def execute(self, command: RefreshSessionCommand) -> AuthTokensResult:
        record = self._refresh_tokens.get_valid_by_plain_token(command.refresh_token)
        if record is None:
            raise InvalidRefreshTokenError()

        user = self._users.get_by_id(record.user_id)
        if user is None or not user.is_active:
            raise InvalidRefreshTokenError()

        self._refresh_tokens.revoke(record)
        return self._issuer.issue(user.id, user.email, user.role)
