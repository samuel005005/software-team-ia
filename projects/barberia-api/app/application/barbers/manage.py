from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.auth.errors import EmailAlreadyExistsError
from app.domain.barbers.errors import BarberNotFoundError
from app.infrastructure.repositories.barber_repository import (
    BarberAdminRecord,
    BarberRepository,
    admin_record_from_user,
)
from app.infrastructure.repositories.user_repository import CreateBarberData, UserRepository
from app.infrastructure.security.password_hasher import hash_password


class ListAllBarbersUseCase:
    def __init__(self, session: Session) -> None:
        self._barbers = BarberRepository(session)

    def execute(self) -> list[BarberAdminRecord]:
        return self._barbers.list_all()


@dataclass(frozen=True)
class CreateBarberCommand:
    email: str
    password: str
    display_name: str
    bio: str | None = None
    photo_url: str | None = None
    is_bookable: bool = True


class CreateBarberUseCase:
    def __init__(self, session: Session) -> None:
        self._users = UserRepository(session)
        self._barbers = BarberRepository(session)

    def execute(self, command: CreateBarberCommand) -> BarberAdminRecord:
        if self._users.get_by_email(command.email):
            raise EmailAlreadyExistsError()

        user = self._users.create_barber(
            CreateBarberData(
                email=command.email,
                password_hash=hash_password(command.password),
                display_name=command.display_name,
                bio=command.bio,
                photo_url=command.photo_url,
                is_bookable=command.is_bookable,
            )
        )
        record = self._barbers.get_barber_user(user.id)
        if record is None:
            raise BarberNotFoundError()
        return admin_record_from_user(record)


@dataclass(frozen=True)
class UpdateBarberCommand:
    user_id: UUID
    display_name: str | None = None
    bio: str | None = None
    photo_url: str | None = None
    is_bookable: bool | None = None
    is_active: bool | None = None


class UpdateBarberUseCase:
    def __init__(self, session: Session) -> None:
        self._users = UserRepository(session)
        self._barbers = BarberRepository(session)

    def execute(self, command: UpdateBarberCommand) -> BarberAdminRecord:
        user = self._barbers.get_barber_user(command.user_id)
        if user is None:
            raise BarberNotFoundError()

        updated = self._users.update_barber_admin(
            user,
            display_name=command.display_name,
            bio=command.bio,
            photo_url=command.photo_url,
            is_bookable=command.is_bookable,
            is_active=command.is_active,
        )
        return admin_record_from_user(updated)
