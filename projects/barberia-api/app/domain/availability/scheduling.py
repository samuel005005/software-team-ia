from datetime import date


def date_to_weekday(target_date: date) -> int:
    """Convierte fecha calendario a weekday del dominio (1=lunes … 7=domingo)."""
    return target_date.weekday() + 1
