from app.domain.availability.errors import ServiceNotAvailableError

__all__ = [
    "AppointmentNotCancellableError",
    "AppointmentNotFoundError",
    "BarberNotAvailableError",
    "CancellationWindowExpiredError",
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


class AppointmentNotFoundError(Exception):
    """La cita no existe o no pertenece al cliente."""


class AppointmentNotCancellableError(Exception):
    """Estado no cancelable o cita ya iniciada."""


class CancellationWindowExpiredError(Exception):
    """Ventana mínima de anticipación para cancelar expirada (RN-08)."""
