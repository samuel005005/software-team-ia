from dataclasses import dataclass
from datetime import date
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.domain.appointments.errors import InvalidScheduleRangeError
from app.infrastructure.repositories.appointment_repository import (
    AppointmentRepository,
    BarberAppointmentRecord,
)


@dataclass(frozen=True)
class ListBarberScheduleQuery:
    barber_user_id: UUID
    from_date: date
    to_date: date


class ListMyBarberScheduleUseCase:
    def __init__(self, session: Session) -> None:
        self._appointments = AppointmentRepository(session)

    def execute(
        self, query: ListBarberScheduleQuery
    ) -> tuple[date, date, list[BarberAppointmentRecord]]:
        if query.to_date < query.from_date:
            raise InvalidScheduleRangeError("end_date must be >= date")
        if (query.to_date - query.from_date).days > 6:
            raise InvalidScheduleRangeError("range cannot exceed 7 days")

        tz = ZoneInfo(get_settings().business_timezone)
        items = self._appointments.list_by_barber_for_date_range(
            query.barber_user_id,
            query.from_date,
            query.to_date,
            tz,
        )
        return query.from_date, query.to_date, items
