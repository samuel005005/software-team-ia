from dataclasses import dataclass
from datetime import time

from sqlalchemy.orm import Session

from app.domain.schedules.errors import InvalidBusinessHoursError
from app.domain.schedules.validation import validate_business_hours_day
from app.infrastructure.repositories.schedule_repository import (
    BusinessHoursRecord,
    ScheduleRepository,
)


@dataclass(frozen=True)
class BusinessHoursDayCommand:
    weekday: int
    open_time: time
    close_time: time
    is_closed: bool


class ListBusinessHoursUseCase:
    def __init__(self, session: Session) -> None:
        self._schedule = ScheduleRepository(session)

    def execute(self) -> list[BusinessHoursRecord]:
        return self._schedule.list_business_hours()


class UpdateBusinessHoursUseCase:
    def __init__(self, session: Session) -> None:
        self._schedule = ScheduleRepository(session)

    def execute(self, items: list[BusinessHoursDayCommand]) -> list[BusinessHoursRecord]:
        if not items:
            raise InvalidBusinessHoursError("Debe enviar al menos un día de la semana")

        weekdays = [item.weekday for item in items]
        if len(weekdays) != len(set(weekdays)):
            raise InvalidBusinessHoursError("No puede haber días de la semana duplicados")

        for item in items:
            validate_business_hours_day(
                weekday=item.weekday,
                open_time=item.open_time,
                close_time=item.close_time,
                is_closed=item.is_closed,
            )

        return self._schedule.replace_business_hours(items)
