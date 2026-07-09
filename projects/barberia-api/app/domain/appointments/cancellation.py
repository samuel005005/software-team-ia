from datetime import datetime, timedelta

from app.domain.enums import AppointmentStatus

CANCELLABLE_STATUSES = frozenset({
    AppointmentStatus.PENDIENTE,
    AppointmentStatus.CONFIRMADA,
})

ADMIN_VOIDABLE_STATUSES = frozenset({
    AppointmentStatus.PENDIENTE,
    AppointmentStatus.CONFIRMADA,
    AppointmentStatus.EN_PROGRESO,
    AppointmentStatus.NO_SHOW,
})


def is_client_cancellable_status(status: AppointmentStatus) -> bool:
    return status in CANCELLABLE_STATUSES


def is_admin_voidable_status(status: AppointmentStatus) -> bool:
    return status in ADMIN_VOIDABLE_STATUSES


def meets_cancellation_notice(
    scheduled_start: datetime,
    now: datetime,
    min_hours: int,
) -> bool:
    return (scheduled_start - now) >= timedelta(hours=min_hours)
