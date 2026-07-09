import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.infrastructure.db.models.barber_service import BarberService
from app.infrastructure.db.models.service import Service
from app.infrastructure.repositories.service_repository import ServiceRecord, _to_service_record


class BarberServiceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def is_assigned(self, barber_user_id: uuid.UUID, service_id: uuid.UUID) -> bool:
        row = self._session.scalar(
            select(BarberService).where(
                BarberService.barber_user_id == barber_user_id,
                BarberService.service_id == service_id,
            )
        )
        return row is not None

    def list_services_for_barber(self, barber_user_id: uuid.UUID) -> list[ServiceRecord]:
        rows = self._session.scalars(
            select(Service)
            .join(BarberService, BarberService.service_id == Service.id)
            .where(BarberService.barber_user_id == barber_user_id)
            .order_by(Service.name)
        ).all()
        return [_to_service_record(row) for row in rows]

    def replace_assignments(
        self,
        barber_user_id: uuid.UUID,
        service_ids: list[uuid.UUID],
    ) -> list[ServiceRecord]:
        unique_ids = list(dict.fromkeys(service_ids))

        if unique_ids:
            valid_services = self._session.scalars(
                select(Service)
                .where(Service.id.in_(unique_ids), Service.is_active.is_(True))
            ).all()
            if len(valid_services) != len(unique_ids):
                raise ValueError("Invalid or inactive services in assignment")

        self._session.execute(
            delete(BarberService).where(BarberService.barber_user_id == barber_user_id)
        )

        for service_id in unique_ids:
            self._session.add(
                BarberService(
                    barber_user_id=barber_user_id,
                    service_id=service_id,
                )
            )
        self._session.flush()

        return self.list_services_for_barber(barber_user_id)
