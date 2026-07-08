from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.auth.errors import EmailAlreadyExistsError
from app.infrastructure.repositories.user_repository import CreateClientData, UserRepository
from app.infrastructure.security.password_hasher import hash_password


@dataclass(frozen=True)
class RegisterClientCommand:
    email: str
    password: str
    full_name: str
    phone: str


@dataclass(frozen=True)
class RegisterClientResult:
    user_id: UUID
    email: str
    full_name: str


class RegisterClientUseCase:
    def __init__(self, session: Session) -> None:
        self._users = UserRepository(session)

    def execute(self, command: RegisterClientCommand) -> RegisterClientResult:
        if self._users.get_by_email(command.email):
            raise EmailAlreadyExistsError()

        user = self._users.create_client(
            CreateClientData(
                email=command.email,
                password_hash=hash_password(command.password),
                full_name=command.full_name,
                phone=command.phone,
            )
        )

        return RegisterClientResult(
            user_id=user.id,
            email=user.email,
            full_name=user.client_profile.full_name if user.client_profile else command.full_name,
        )
