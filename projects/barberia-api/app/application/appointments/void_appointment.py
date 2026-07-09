from dataclasses import dataclass
from datetime import datetime
import uuid
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.domain.appointments.cancellation import is_admin_voidable_status
from app.domain.appointments.errors import (
    AppointmentNotCancellableError,
    AppointmentNotFoundError,
)
from app.infrastructure.repositories.appointment_repository import (
    AppointmentDetailRecord,
    AppointmentRepository,
)
from app.infrastructure.repositories.audit_log_repository import AuditLogRepository


@dataclass(frozen=True)
class VoidAppointmentCommand:
    appointment_id: uuid.UUID
    admin_user_id: uuid.UUID
    reason: str
    now: datetime


def _normalize_to_business_tz(value: datetime, tz: ZoneInfo) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=tz)
    return value.astimezone(tz)


class VoidAppointmentUseCase:
    def __init__(self, session: Session) -> None:
        self._appointments = AppointmentRepository(session)
        self._audit_logs = AuditLogRepository(session)
        self._settings = get_settings()

    def execute(self, command: VoidAppointmentCommand) -> AppointmentDetailRecord:
        tz = ZoneInfo(self._settings.business_timezone)
        now = _normalize_to_business_tz(command.now, tz)
        reason = command.reason.strip()
        if len(reason) < 3:
            raise AppointmentNotCancellableError()

        appointment = self._appointments.get_by_id(command.appointment_id)
        if appointment is None:
            raise AppointmentNotFoundError()

        if not is_admin_voidable_status(appointment.status):
            raise AppointmentNotCancellableError()

        from_status = appointment.status
        self._appointments.cancel(
            appointment,
            cancelled_at=now,
            changed_by_user_id=command.admin_user_id,
            cancellation_reason=reason,
        )
        self._audit_logs.log_appointment_voided(
            actor_user_id=command.admin_user_id,
            appointment_id=appointment.id,
            from_status=from_status,
            reason=reason,
        )

        detail = self._appointments.to_detail_record(appointment)
        if detail is None:
            raise AppointmentNotFoundError()

        return detail
