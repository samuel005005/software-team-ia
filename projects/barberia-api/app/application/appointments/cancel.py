from dataclasses import dataclass
from datetime import datetime
import uuid
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.domain.appointments.cancellation import (
    is_client_cancellable_status,
    meets_cancellation_notice,
)
from app.domain.appointments.errors import (
    AppointmentNotCancellableError,
    AppointmentNotFoundError,
    CancellationWindowExpiredError,
)
from app.infrastructure.repositories.appointment_repository import (
    AppointmentDetailRecord,
    AppointmentRepository,
)


@dataclass(frozen=True)
class CancelAppointmentCommand:
    appointment_id: uuid.UUID
    client_user_id: uuid.UUID
    now: datetime


def _normalize_to_business_tz(value: datetime, tz: ZoneInfo) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=tz)
    return value.astimezone(tz)


class CancelAppointmentUseCase:
    def __init__(self, session: Session) -> None:
        self._appointments = AppointmentRepository(session)
        self._settings = get_settings()

    def execute(self, command: CancelAppointmentCommand) -> AppointmentDetailRecord:
        tz = ZoneInfo(self._settings.business_timezone)
        now = _normalize_to_business_tz(command.now, tz)

        appointment = self._appointments.get_by_id(command.appointment_id)
        if appointment is None or appointment.client_user_id != command.client_user_id:
            raise AppointmentNotFoundError()

        if not is_client_cancellable_status(appointment.status):
            raise AppointmentNotCancellableError()

        if appointment.scheduled_start <= now:
            raise AppointmentNotCancellableError()

        if not meets_cancellation_notice(
            appointment.scheduled_start,
            now,
            self._settings.cancellation_notice_hours,
        ):
            raise CancellationWindowExpiredError()

        self._appointments.cancel(appointment, cancelled_at=now)

        detail = self._appointments.to_detail_record(appointment)
        if detail is None:
            raise AppointmentNotFoundError()

        return detail
