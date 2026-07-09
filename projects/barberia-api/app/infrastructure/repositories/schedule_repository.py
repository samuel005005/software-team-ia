from dataclasses import dataclass
from datetime import time
import uuid
from typing import Protocol

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.infrastructure.db.models.schedule import BarberAvailability, BusinessHours


class BusinessHoursInput(Protocol):
    weekday: int
    open_time: time
    close_time: time
    is_closed: bool


class BarberAvailabilityInput(Protocol):
    weekday: int
    start_time: time
    end_time: time
    is_active: bool


@dataclass(frozen=True)
class BusinessHoursRecord:
    weekday: int
    open_time: time
    close_time: time
    is_closed: bool


@dataclass(frozen=True)
class BarberAvailabilityRecord:
    weekday: int
    start_time: time
    end_time: time
    is_active: bool


class ScheduleRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_business_hours(self, weekday: int) -> BusinessHoursRecord | None:
        row = self._session.scalar(
            select(BusinessHours).where(BusinessHours.weekday == weekday)
        )
        if row is None:
            return None
        return self._to_record(row)

    def list_business_hours(self) -> list[BusinessHoursRecord]:
        rows = self._session.scalars(
            select(BusinessHours).order_by(BusinessHours.weekday.asc())
        ).all()
        return [self._to_record(row) for row in rows]

    def replace_business_hours(
        self,
        items: list[BusinessHoursInput],
    ) -> list[BusinessHoursRecord]:
        self._session.execute(delete(BusinessHours))
        for item in sorted(items, key=lambda entry: entry.weekday):
            self._session.add(
                BusinessHours(
                    weekday=item.weekday,
                    open_time=item.open_time,
                    close_time=item.close_time,
                    is_closed=item.is_closed,
                )
            )
        self._session.flush()
        return self.list_business_hours()

    @staticmethod
    def _to_record(row: BusinessHours) -> BusinessHoursRecord:
        return BusinessHoursRecord(
            weekday=row.weekday,
            open_time=row.open_time,
            close_time=row.close_time,
            is_closed=row.is_closed,
        )

    def get_barber_availability_for_weekday(
        self,
        barber_user_id: uuid.UUID,
        weekday: int,
    ) -> BarberAvailabilityRecord | None:
        row = self._session.scalar(
            select(BarberAvailability).where(
                BarberAvailability.barber_user_id == barber_user_id,
                BarberAvailability.weekday == weekday,
                BarberAvailability.is_active.is_(True),
            )
        )
        if row is None:
            return None
        return self._to_availability_record(row)

    def barber_ids_with_availability_on_weekday(self, weekday: int) -> set[uuid.UUID]:
        rows = self._session.scalars(
            select(BarberAvailability.barber_user_id).where(
                BarberAvailability.weekday == weekday,
                BarberAvailability.is_active.is_(True),
            )
        ).all()
        return set(rows)

    def list_barber_availability(
        self,
        barber_user_id: uuid.UUID,
    ) -> list[BarberAvailabilityRecord]:
        rows = self._session.scalars(
            select(BarberAvailability)
            .where(BarberAvailability.barber_user_id == barber_user_id)
            .order_by(BarberAvailability.weekday.asc())
        ).all()
        return [self._to_availability_record(row) for row in rows]

    def replace_barber_availability(
        self,
        barber_user_id: uuid.UUID,
        items: list[BarberAvailabilityInput],
    ) -> list[BarberAvailabilityRecord]:
        self._session.execute(
            delete(BarberAvailability).where(
                BarberAvailability.barber_user_id == barber_user_id
            )
        )
        for item in sorted(items, key=lambda entry: entry.weekday):
            self._session.add(
                BarberAvailability(
                    barber_user_id=barber_user_id,
                    weekday=item.weekday,
                    start_time=item.start_time,
                    end_time=item.end_time,
                    is_active=item.is_active,
                )
            )
        self._session.flush()
        return self.list_barber_availability(barber_user_id)

    @staticmethod
    def _to_availability_record(row: BarberAvailability) -> BarberAvailabilityRecord:
        return BarberAvailabilityRecord(
            weekday=row.weekday,
            start_time=row.start_time,
            end_time=row.end_time,
            is_active=row.is_active,
        )
