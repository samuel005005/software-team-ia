from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.users.errors import ClientNotFoundError
from app.infrastructure.repositories.appointment_repository import (
    AppointmentRepository,
    ClientAppointmentRecord,
)
from app.infrastructure.repositories.client_repository import (
    ClientAdminRecord,
    ClientRepository,
    admin_record_from_user,
)
from app.infrastructure.repositories.user_repository import UserRepository


class ListAllClientsUseCase:
    def __init__(self, session: Session) -> None:
        self._clients = ClientRepository(session)

    def execute(self) -> list[ClientAdminRecord]:
        return self._clients.list_all()


@dataclass(frozen=True)
class UpdateClientCommand:
    user_id: UUID
    is_active: bool | None = None


class UpdateClientUseCase:
    def __init__(self, session: Session) -> None:
        self._clients = ClientRepository(session)
        self._users = UserRepository(session)

    def execute(self, command: UpdateClientCommand) -> ClientAdminRecord:
        user = self._clients.get_client_user(command.user_id)
        if user is None:
            raise ClientNotFoundError()

        updated = self._users.update_client_admin(
            user,
            is_active=command.is_active,
        )
        return admin_record_from_user(updated)


class ListClientAppointmentsUseCase:
    def __init__(self, session: Session) -> None:
        self._clients = ClientRepository(session)
        self._appointments = AppointmentRepository(session)

    def execute(self, client_user_id: UUID) -> list[ClientAppointmentRecord]:
        user = self._clients.get_client_user(client_user_id)
        if user is None:
            raise ClientNotFoundError()

        return self._appointments.list_by_client(client_user_id)
