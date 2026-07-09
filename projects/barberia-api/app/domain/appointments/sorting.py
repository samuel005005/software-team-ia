from datetime import datetime

from app.infrastructure.repositories.appointment_repository import ClientAppointmentRecord


def sort_client_appointments(
    appointments: list[ClientAppointmentRecord],
    now: datetime,
) -> list[ClientAppointmentRecord]:
    upcoming = [a for a in appointments if a.scheduled_start >= now]
    past = [a for a in appointments if a.scheduled_start < now]
    upcoming.sort(key=lambda a: a.scheduled_start)
    past.sort(key=lambda a: a.scheduled_start, reverse=True)
    return upcoming + past
