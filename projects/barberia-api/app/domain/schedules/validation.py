from datetime import time


def validate_business_hours_day(
    *,
    weekday: int,
    open_time: time,
    close_time: time,
    is_closed: bool,
) -> None:
    from app.domain.schedules.errors import InvalidBusinessHoursError

    if weekday < 1 or weekday > 7:
        raise InvalidBusinessHoursError("El día de la semana debe estar entre 1 y 7")

    if not is_closed and open_time >= close_time:
        raise InvalidBusinessHoursError(
            "La hora de apertura debe ser anterior a la hora de cierre"
        )


def validate_barber_availability_block(
    *,
    weekday: int,
    start_time: time,
    end_time: time,
    is_active: bool,
) -> None:
    from app.domain.schedules.errors import InvalidBarberAvailabilityError

    if weekday < 1 or weekday > 7:
        raise InvalidBarberAvailabilityError("El día de la semana debe estar entre 1 y 7")

    if is_active and start_time >= end_time:
        raise InvalidBarberAvailabilityError(
            "La hora de inicio debe ser anterior a la hora de fin"
        )
