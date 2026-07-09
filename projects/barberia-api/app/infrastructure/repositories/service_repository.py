from dataclasses import dataclass
from decimal import Decimal
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.db.models.service import Service


@dataclass(frozen=True)
class ServiceRecord:
    id: str
    name: str
    description: str | None
    duration_minutes: int
    price_dop: str
    is_active: bool


class ServiceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_active(self) -> list[ServiceRecord]:
        rows = self._session.scalars(
            select(Service)
            .where(Service.is_active.is_(True))
            .order_by(Service.name)
        ).all()
        return [_to_service_record(row) for row in rows]

    def list_all(self) -> list[ServiceRecord]:
        rows = self._session.scalars(select(Service).order_by(Service.name)).all()
        return [_to_service_record(row) for row in rows]

    def get_by_id(self, service_id: uuid.UUID) -> Service | None:
        return self._session.get(Service, service_id)

    def create(
        self,
        *,
        name: str,
        description: str | None,
        duration_minutes: int,
        price_dop: Decimal,
        is_active: bool = True,
    ) -> Service:
        service = Service(
            name=name.strip(),
            description=description.strip() if description else None,
            duration_minutes=duration_minutes,
            price_dop=price_dop,
            is_active=is_active,
        )
        self._session.add(service)
        self._session.flush()
        return service

    def update(
        self,
        service: Service,
        *,
        name: str | None = None,
        description: str | None = None,
        duration_minutes: int | None = None,
        price_dop: Decimal | None = None,
        is_active: bool | None = None,
    ) -> Service:
        if name is not None:
            service.name = name.strip()
        if description is not None:
            service.description = description.strip() or None
        if duration_minutes is not None:
            service.duration_minutes = duration_minutes
        if price_dop is not None:
            service.price_dop = price_dop
        if is_active is not None:
            service.is_active = is_active
        self._session.flush()
        return service


def _to_service_record(row: Service) -> ServiceRecord:
    price = row.price_dop
    if isinstance(price, Decimal):
        price_text = format(price, "f")
    else:
        price_text = str(price)

    return ServiceRecord(
        id=str(row.id),
        name=row.name,
        description=row.description,
        duration_minutes=row.duration_minutes,
        price_dop=price_text,
        is_active=row.is_active,
    )
