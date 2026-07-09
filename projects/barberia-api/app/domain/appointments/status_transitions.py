from app.domain.enums import AppointmentStatus

BARBER_ALLOWED_TRANSITIONS: dict[AppointmentStatus, frozenset[AppointmentStatus]] = {
    AppointmentStatus.PENDIENTE: frozenset({
        AppointmentStatus.CONFIRMADA,
        AppointmentStatus.NO_SHOW,
    }),
    AppointmentStatus.CONFIRMADA: frozenset({
        AppointmentStatus.EN_PROGRESO,
        AppointmentStatus.NO_SHOW,
    }),
    AppointmentStatus.EN_PROGRESO: frozenset({
        AppointmentStatus.COMPLETADA,
    }),
}


def can_barber_transition(
    from_status: AppointmentStatus,
    to_status: AppointmentStatus,
) -> bool:
    return to_status in BARBER_ALLOWED_TRANSITIONS.get(from_status, frozenset())
