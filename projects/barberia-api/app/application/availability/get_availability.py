from dataclasses import dataclass
from datetime import date, datetime
import uuid
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.application.availability.list_available_barbers import ListAvailableBarbersUseCase
from app.core.config import get_settings
from app.domain.availability.scheduling import date_to_weekday
from app.domain.availability.slots import (
    BlockingInterval,
    filter_available_slots,
    generate_slot_candidates,
    intersect_time_windows,
)
from app.infrastructure.repositories.appointment_repository import AppointmentRepository
from app.infrastructure.repositories.barber_repository import BarberPublicProfile
from app.infrastructure.repositories.schedule_repository import ScheduleRepository
from app.infrastructure.repositories.service_repository import ServiceRepository
from app.schemas.availability import AvailabilitySlot


@dataclass(frozen=True)
class AvailabilityResult:
    barbers: list[BarberPublicProfile]
    slots: list[AvailabilitySlot]


class GetAvailabilityUseCase:
    def __init__(self, session: Session) -> None:
        self._services = ServiceRepository(session)
        self._schedule = ScheduleRepository(session)
        self._appointments = AppointmentRepository(session)
        self._list_barbers = ListAvailableBarbersUseCase(session)
        self._settings = get_settings()

    def execute(
        self,
        service_id: uuid.UUID,
        target_date: date,
        barber_id: uuid.UUID | None = None,
    ) -> AvailabilityResult:
        barbers = self._list_barbers.execute(service_id, target_date)

        if barber_id is not None:
            barber_id_text = str(barber_id)
            barbers = [barber for barber in barbers if barber.user_id == barber_id_text]

        if not barbers:
            return AvailabilityResult(barbers=[], slots=[])

        service = self._services.get_by_id(service_id)
        if service is None:
            return AvailabilityResult(barbers=[], slots=[])

        weekday = date_to_weekday(target_date)
        business_hours = self._schedule.get_business_hours(weekday)
        tz = ZoneInfo(self._settings.business_timezone)
        now = datetime.now(tz)

        slots: list[AvailabilitySlot] = []

        for barber in barbers:
            barber_uuid = uuid.UUID(barber.user_id)
            availability = self._schedule.get_barber_availability_for_weekday(
                barber_uuid,
                weekday,
            )
            if availability is None:
                continue

            if business_hours is not None and not business_hours.is_closed:
                window = intersect_time_windows(
                    availability.start_time,
                    availability.end_time,
                    business_hours.open_time,
                    business_hours.close_time,
                )
            else:
                window = (availability.start_time, availability.end_time)

            if window is None:
                continue

            window_start, window_end = window
            candidates = generate_slot_candidates(
                window_start,
                window_end,
                service.duration_minutes,
            )

            blocking_records = self._appointments.list_blocking_for_barber_on_date(
                barber_uuid,
                target_date,
                tz,
            )
            blocking = [
                BlockingInterval(
                    start=record.scheduled_start,
                    end=record.scheduled_end,
                )
                for record in blocking_records
            ]

            for slot in filter_available_slots(
                candidates,
                blocking,
                now,
                target_date,
                tz,
            ):
                slots.append(
                    AvailabilitySlot(
                        start=slot.start,
                        end=slot.end,
                        barber_user_id=barber.user_id,
                    )
                )

        slots.sort(key=lambda entry: entry.start)
        return AvailabilityResult(barbers=barbers, slots=slots)
