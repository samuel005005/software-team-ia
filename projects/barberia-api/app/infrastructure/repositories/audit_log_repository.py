import uuid

from sqlalchemy.orm import Session

from app.domain.enums import AppointmentStatus
from app.infrastructure.db.models.appointment import AuditLog


class AuditLogRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def log_appointment_voided(
        self,
        *,
        actor_user_id: uuid.UUID,
        appointment_id: uuid.UUID,
        from_status: AppointmentStatus,
        reason: str,
    ) -> None:
        log = AuditLog(
            actor_user_id=actor_user_id,
            action="appointment_voided",
            entity_type="appointment",
            entity_id=appointment_id,
            metadata_json={
                "reason": reason,
                "from_status": from_status.value,
            },
        )
        self._session.add(log)
