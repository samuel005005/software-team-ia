from dataclasses import dataclass
from datetime import datetime
import uuid
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.domain.appointments.errors import (
    BarberNotAvailableError,
    PastAppointmentError,
    ServiceNotAvailableError,
    SlotNotAvailableError,
)
from app.domain.appointments.scheduling import calculate_scheduled_end
from app.domain.appointments.validation import is_bookable_slot
from app.domain.availability.scheduling import date_to_weekday
from app.domain.availability.slots import BlockingInterval
from app.domain.enums import AppointmentStatus
from app.infrastructure.repositories.appointment_repository import (
    AppointmentDetailRecord,
    AppointmentRepository,
)
from app.infrastructure.repositories.barber_repository import BarberRepository
from app.infrastructure.repositories.barber_service_repository import BarberServiceRepository
from app.infrastructure.repositories.schedule_repository import ScheduleRepository
from app.infrastructure.repositories.service_repository import ServiceRepository


@dataclass(frozen=True)
class CreateAppointmentCommand:
    client_user_id: uuid.UUID
    barber_user_id: uuid.UUID
    service_id: uuid.UUID
    scheduled_start: datetime


def _normalize_to_business_tz(value: datetime, tz: ZoneInfo) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=tz)
    return value.astimezone(tz)


class CreateAppointmentUseCase:
    def __init__(self, session: Session) -> None:
        self._services = ServiceRepository(session)
        self._barbers = BarberRepository(session)
        self._schedule = ScheduleRepository(session)
        self._appointments = AppointmentRepository(session)
        self._barber_services = BarberServiceRepository(session)
        self._settings = get_settings()

    def execute(self, command: CreateAppointmentCommand) -> AppointmentDetailRecord:
        tz = ZoneInfo(self._settings.business_timezone)
        now = datetime.now(tz)
        scheduled_start = _normalize_to_business_tz(command.scheduled_start, tz)

        if scheduled_start <= now:
            raise PastAppointmentError()

        service = self._services.get_by_id(command.service_id)
        if service is None or not service.is_active:
            raise ServiceNotAvailableError()

        scheduled_end = calculate_scheduled_end(scheduled_start, service.duration_minutes)

        barber_user = self._barbers.get_barber_user(command.barber_user_id)
        if barber_user is None or not barber_user.is_active:
            raise BarberNotAvailableError()

        profile = barber_user.barber_profile
        if profile is None or not profile.is_bookable:
            raise BarberNotAvailableError()

        if not self._barber_services.is_assigned(command.barber_user_id, command.service_id):
            raise BarberNotAvailableError()

        target_date = scheduled_start.date()
        weekday = date_to_weekday(target_date)

        availability = self._schedule.get_barber_availability_for_weekday(
            command.barber_user_id,
            weekday,
        )
        barber_window = None
        if availability is not None:
            barber_window = (availability.start_time, availability.end_time)

        business_hours = self._schedule.get_business_hours(weekday)
        business_window = None
        if business_hours is not None and not business_hours.is_closed:
            business_window = (business_hours.open_time, business_hours.close_time)

        blocking_records = self._appointments.list_blocking_for_barber_on_date(
            command.barber_user_id,
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

        if not is_bookable_slot(
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            service_duration_minutes=service.duration_minutes,
            barber_window=barber_window,
            business_window=business_window,
            blocking=blocking,
            now=now,
        ):
            raise SlotNotAvailableError()

        self._appointments.lock_blocking_for_barber_in_range(
            command.barber_user_id,
            scheduled_start,
            scheduled_end,
        )

        try:
            appointment = self._appointments.create(
                client_user_id=command.client_user_id,
                barber_user_id=command.barber_user_id,
                service_id=command.service_id,
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                status=AppointmentStatus.CONFIRMADA,
            )
        except IntegrityError as exc:
            raise SlotNotAvailableError() from exc

        return AppointmentDetailRecord(
            id=str(appointment.id),
            status=appointment.status,
            scheduled_start=appointment.scheduled_start,
            scheduled_end=appointment.scheduled_end,
            service_id=str(service.id),
            service_name=service.name,
            barber_user_id=str(barber_user.id),
            barber_display_name=profile.display_name,
        )
