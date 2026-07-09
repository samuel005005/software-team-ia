from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.barbers.errors import BarberNotFoundError, InvalidServiceAssignmentError
from app.infrastructure.repositories.barber_repository import BarberRepository
from app.infrastructure.repositories.barber_service_repository import BarberServiceRepository
from app.infrastructure.repositories.service_repository import ServiceRecord


class GetBarberServicesUseCase:
    def __init__(self, session: Session) -> None:
        self._barbers = BarberRepository(session)
        self._assignments = BarberServiceRepository(session)

    def execute(self, barber_user_id: UUID) -> list[ServiceRecord]:
        if self._barbers.get_barber_user(barber_user_id) is None:
            raise BarberNotFoundError()
        return self._assignments.list_services_for_barber(barber_user_id)


@dataclass(frozen=True)
class SetBarberServicesCommand:
    barber_user_id: UUID
    service_ids: list[UUID]


class SetBarberServicesUseCase:
    def __init__(self, session: Session) -> None:
        self._barbers = BarberRepository(session)
        self._assignments = BarberServiceRepository(session)

    def execute(self, command: SetBarberServicesCommand) -> list[ServiceRecord]:
        if self._barbers.get_barber_user(command.barber_user_id) is None:
            raise BarberNotFoundError()

        try:
            return self._assignments.replace_assignments(
                command.barber_user_id,
                command.service_ids,
            )
        except ValueError as exc:
            raise InvalidServiceAssignmentError() from exc
