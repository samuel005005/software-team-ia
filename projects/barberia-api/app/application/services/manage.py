from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.services.errors import ServiceNotFoundError
from app.infrastructure.repositories.service_repository import ServiceRecord, ServiceRepository


class ListAllServicesUseCase:
    def __init__(self, session: Session) -> None:
        self._services = ServiceRepository(session)

    def execute(self) -> list[ServiceRecord]:
        return self._services.list_all()


@dataclass(frozen=True)
class CreateServiceCommand:
    name: str
    duration_minutes: int
    price_dop: Decimal
    description: str | None = None
    is_active: bool = True


class CreateServiceUseCase:
    def __init__(self, session: Session) -> None:
        self._services = ServiceRepository(session)

    def execute(self, command: CreateServiceCommand) -> ServiceRecord:
        service = self._services.create(
            name=command.name,
            description=command.description,
            duration_minutes=command.duration_minutes,
            price_dop=command.price_dop,
            is_active=command.is_active,
        )
        return ServiceRecord(
            id=str(service.id),
            name=service.name,
            description=service.description,
            duration_minutes=service.duration_minutes,
            price_dop=format(service.price_dop, "f"),
            is_active=service.is_active,
        )


@dataclass(frozen=True)
class UpdateServiceCommand:
    service_id: UUID
    name: str | None = None
    description: str | None = None
    duration_minutes: int | None = None
    price_dop: Decimal | None = None
    is_active: bool | None = None


class UpdateServiceUseCase:
    def __init__(self, session: Session) -> None:
        self._services = ServiceRepository(session)

    def execute(self, command: UpdateServiceCommand) -> ServiceRecord:
        service = self._services.get_by_id(command.service_id)
        if service is None:
            raise ServiceNotFoundError()

        updated = self._services.update(
            service,
            name=command.name,
            description=command.description,
            duration_minutes=command.duration_minutes,
            price_dop=command.price_dop,
            is_active=command.is_active,
        )
        return ServiceRecord(
            id=str(updated.id),
            name=updated.name,
            description=updated.description,
            duration_minutes=updated.duration_minutes,
            price_dop=format(updated.price_dop, "f"),
            is_active=updated.is_active,
        )
