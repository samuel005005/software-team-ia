from datetime import datetime, timedelta


def calculate_scheduled_end(scheduled_start: datetime, duration_minutes: int) -> datetime:
    """Calcula scheduled_end a partir de la duración del servicio (RN-03, T-025)."""
    if duration_minutes <= 0:
        raise ValueError("duration_minutes must be positive")
    return scheduled_start + timedelta(minutes=duration_minutes)
