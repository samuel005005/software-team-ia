from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
import uuid
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import AppointmentStatus
from app.infrastructure.db.models.appointment import Appointment
from app.infrastructure.db.models.barber_profile import BarberProfile
from app.infrastructure.db.models.service import Service


@dataclass(frozen=True)
class BlockingAppointmentRecord:
    scheduled_start: datetime
    scheduled_end: datetime


@dataclass(frozen=True)
class AppointmentDetailRecord:
    id: str
    status: AppointmentStatus
    scheduled_start: datetime
    scheduled_end: datetime
    service_id: str
    service_name: str
    barber_user_id: str
    barber_display_name: str


@dataclass(frozen=True)
class ClientAppointmentRecord:
    id: str
    status: AppointmentStatus
    scheduled_start: datetime
    scheduled_end: datetime
    service_id: str
    service_name: str
    barber_user_id: str
    barber_display_name: str


class AppointmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        client_user_id: uuid.UUID,
        barber_user_id: uuid.UUID,
        service_id: uuid.UUID,
        scheduled_start: datetime,
        scheduled_end: datetime,
        status: AppointmentStatus,
    ) -> Appointment:
        appointment = Appointment(
            client_user_id=client_user_id,
            barber_user_id=barber_user_id,
            service_id=service_id,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            status=status,
        )
        self._session.add(appointment)
        self._session.flush()
        return appointment

    def get_by_id(self, appointment_id: uuid.UUID) -> Appointment | None:
        return self._session.get(Appointment, appointment_id)

    def cancel(self, appointment: Appointment, *, cancelled_at: datetime) -> None:
        appointment.status = AppointmentStatus.CANCELADA
        appointment.cancelled_at = cancelled_at
        self._session.flush()

    def to_detail_record(self, appointment: Appointment) -> AppointmentDetailRecord | None:
        service = self._session.get(Service, appointment.service_id)
        barber = self._session.scalar(
            select(BarberProfile).where(BarberProfile.user_id == appointment.barber_user_id)
        )
        if service is None or barber is None:
            return None

        return AppointmentDetailRecord(
            id=str(appointment.id),
            status=appointment.status,
            scheduled_start=appointment.scheduled_start,
            scheduled_end=appointment.scheduled_end,
            service_id=str(service.id),
            service_name=service.name,
            barber_user_id=str(appointment.barber_user_id),
            barber_display_name=barber.display_name,
        )

    def lock_blocking_for_barber_in_range(
        self,
        barber_user_id: uuid.UUID,
        range_start: datetime,
        range_end: datetime,
    ) -> None:
        self._session.scalars(
            select(Appointment)
            .where(
                Appointment.barber_user_id == barber_user_id,
                Appointment.status != AppointmentStatus.CANCELADA,
                Appointment.scheduled_start < range_end,
                Appointment.scheduled_end > range_start,
            )
            .with_for_update()
        ).all()

    def list_blocking_for_barber_on_date(
        self,
        barber_user_id: uuid.UUID,
        target_date: date,
        tz: ZoneInfo,
    ) -> list[BlockingAppointmentRecord]:
        day_start = datetime.combine(target_date, time.min, tzinfo=tz)
        day_end = day_start + timedelta(days=1)

        rows = self._session.scalars(
            select(Appointment).where(
                Appointment.barber_user_id == barber_user_id,
                Appointment.status != AppointmentStatus.CANCELADA,
                Appointment.scheduled_start < day_end,
                Appointment.scheduled_end > day_start,
            )
        ).all()

        return [
            BlockingAppointmentRecord(
                scheduled_start=row.scheduled_start,
                scheduled_end=row.scheduled_end,
            )
            for row in rows
        ]

    def list_by_client(self, client_user_id: uuid.UUID) -> list[ClientAppointmentRecord]:
        rows = self._session.scalars(
            select(Appointment)
            .where(Appointment.client_user_id == client_user_id)
            .order_by(Appointment.scheduled_start.desc())
        ).all()

        if not rows:
            return []

        service_ids = {row.service_id for row in rows}
        barber_ids = {row.barber_user_id for row in rows}

        services = {
            service.id: service
            for service in self._session.scalars(
                select(Service).where(Service.id.in_(service_ids))
            ).all()
        }
        barbers = {
            barber.user_id: barber
            for barber in self._session.scalars(
                select(BarberProfile).where(BarberProfile.user_id.in_(barber_ids))
            ).all()
        }

        return [
            ClientAppointmentRecord(
                id=str(row.id),
                status=row.status,
                scheduled_start=row.scheduled_start,
                scheduled_end=row.scheduled_end,
                service_id=str(row.service_id),
                service_name=services[row.service_id].name,
                barber_user_id=str(row.barber_user_id),
                barber_display_name=barbers[row.barber_user_id].display_name,
            )
            for row in rows
            if row.service_id in services and row.barber_user_id in barbers
        ]
