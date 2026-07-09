from dataclasses import dataclass
from datetime import datetime
import uuid
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.domain.appointments.errors import (
    AppointmentNotFoundError,
    AppointmentNotUpdatableError,
    InvalidStatusTransitionError,
)
from app.domain.appointments.status_transitions import can_barber_transition
from app.domain.enums import AppointmentStatus
from app.infrastructure.repositories.appointment_repository import (
    AppointmentRepository,
    BarberAppointmentRecord,
)


@dataclass(frozen=True)
class UpdateBarberAppointmentStatusCommand:
    appointment_id: uuid.UUID
    barber_user_id: uuid.UUID
    new_status: AppointmentStatus
    now: datetime


def _normalize_to_business_tz(value: datetime, tz: ZoneInfo) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=tz)
    return value.astimezone(tz)


class UpdateBarberAppointmentStatusUseCase:
    def __init__(self, session: Session) -> None:
        self._appointments = AppointmentRepository(session)
        self._settings = get_settings()

    def execute(
        self,
        command: UpdateBarberAppointmentStatusCommand,
    ) -> BarberAppointmentRecord:
        tz = ZoneInfo(self._settings.business_timezone)
        now = _normalize_to_business_tz(command.now, tz)

        appointment = self._appointments.get_by_id(command.appointment_id)
        if appointment is None or appointment.barber_user_id != command.barber_user_id:
            raise AppointmentNotFoundError()

        current_status = appointment.status

        if current_status == command.new_status:
            raise InvalidStatusTransitionError()

        if current_status in {
            AppointmentStatus.COMPLETADA,
            AppointmentStatus.CANCELADA,
            AppointmentStatus.NO_SHOW,
        }:
            raise AppointmentNotUpdatableError()

        if not can_barber_transition(current_status, command.new_status):
            raise InvalidStatusTransitionError()

        if command.new_status == AppointmentStatus.NO_SHOW:
            if now < appointment.scheduled_start:
                raise InvalidStatusTransitionError()

        self._appointments.update_status(
            appointment,
            new_status=command.new_status,
            changed_by_user_id=command.barber_user_id,
            changed_at=now,
        )

        record = self._appointments.to_barber_record(appointment)
        if record is None:
            raise AppointmentNotFoundError()

        return record
