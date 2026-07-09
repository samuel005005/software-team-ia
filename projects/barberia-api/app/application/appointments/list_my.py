from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.appointments.sorting import sort_client_appointments
from app.domain.enums import UserRole
from app.infrastructure.repositories.appointment_repository import (
    AppointmentRepository,
    ClientAppointmentRecord,
)


@dataclass(frozen=True)
class ListMyAppointmentsQuery:
    user_id: UUID
    role: UserRole
    now: datetime


class ListMyAppointmentsUseCase:
    def __init__(self, session: Session) -> None:
        self._appointments = AppointmentRepository(session)

    def execute(self, query: ListMyAppointmentsQuery) -> list[ClientAppointmentRecord]:
        if query.role != UserRole.CLIENT:
            return []

        raw = self._appointments.list_by_client(query.user_id)
        return sort_client_appointments(raw, query.now)
