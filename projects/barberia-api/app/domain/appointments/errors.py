from app.domain.availability.errors import ServiceNotAvailableError

__all__ = [
    "BarberNotAvailableError",
    "PastAppointmentError",
    "ServiceNotAvailableError",
    "SlotNotAvailableError",
]


class BarberNotAvailableError(Exception):
    """Barbero inactivo, no reservable o sin el servicio asignado."""


class SlotNotAvailableError(Exception):
    """Slot ocupado, fuera de disponibilidad o no alineado con la granularidad."""


class PastAppointmentError(Exception):
    """La fecha/hora de inicio está en el pasado."""
