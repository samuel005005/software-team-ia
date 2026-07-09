from dataclasses import dataclass
from datetime import time
import uuid

from sqlalchemy.orm import Session

from app.domain.schedules.errors import InvalidBarberAvailabilityError
from app.domain.schedules.validation import validate_barber_availability_block
from app.infrastructure.repositories.schedule_repository import (
    BarberAvailabilityRecord,
    ScheduleRepository,
)


@dataclass(frozen=True)
class BarberAvailabilityBlockCommand:
    weekday: int
    start_time: time
    end_time: time
    is_active: bool


class ListMyBarberAvailabilityUseCase:
    def __init__(self, session: Session) -> None:
        self._schedule = ScheduleRepository(session)

    def execute(self, barber_user_id: uuid.UUID) -> list[BarberAvailabilityRecord]:
        return self._schedule.list_barber_availability(barber_user_id)


class UpdateMyBarberAvailabilityUseCase:
    def __init__(self, session: Session) -> None:
        self._schedule = ScheduleRepository(session)

    def execute(
        self,
        barber_user_id: uuid.UUID,
        items: list[BarberAvailabilityBlockCommand],
    ) -> list[BarberAvailabilityRecord]:
        if not items:
            raise InvalidBarberAvailabilityError(
                "Debe enviar al menos un día de la semana"
            )

        weekdays = [item.weekday for item in items]
        if len(weekdays) != len(set(weekdays)):
            raise InvalidBarberAvailabilityError(
                "No puede haber días de la semana duplicados"
            )

        for item in items:
            validate_barber_availability_block(
                weekday=item.weekday,
                start_time=item.start_time,
                end_time=item.end_time,
                is_active=item.is_active,
            )

        return self._schedule.replace_barber_availability(barber_user_id, items)
