from app.domain.availability.errors import ServiceNotAvailableError

__all__ = [
    "AppointmentNotCancellableError",
    "AppointmentNotFoundError",
    "AppointmentNotUpdatableError",
    "BarberNotAvailableError",
    "CancellationWindowExpiredError",
    "InvalidScheduleRangeError",
    "InvalidStatusTransitionError",
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
    """La cita no existe o no pertenece al actor."""


class InvalidStatusTransitionError(Exception):
    """Transición de estado no permitida para el barbero."""


class AppointmentNotUpdatableError(Exception):
    """Cita en estado terminal o no gestionable."""


class AppointmentNotCancellableError(Exception):
    """Estado no cancelable o cita ya iniciada."""


class CancellationWindowExpiredError(Exception):
    """Ventana mínima de anticipación para cancelar expirada (RN-08)."""


class InvalidScheduleRangeError(Exception):
    """Rango de fechas inválido para la agenda del barbero."""
