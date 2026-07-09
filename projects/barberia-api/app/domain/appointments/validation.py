from datetime import datetime, time

from app.domain.availability.slots import (
    BlockingInterval,
    generate_slot_candidates,
    intersect_time_windows,
    is_slot_available,
)


def is_bookable_slot(
    *,
    scheduled_start: datetime,
    scheduled_end: datetime,
    service_duration_minutes: int,
    barber_window: tuple[time, time] | None,
    business_window: tuple[time, time] | None,
    blocking: list[BlockingInterval],
    now: datetime,
) -> bool:
    if scheduled_start <= now:
        return False

    if barber_window is None:
        return False

    if business_window is not None:
        window = intersect_time_windows(
            barber_window[0],
            barber_window[1],
            business_window[0],
            business_window[1],
        )
    else:
        window = barber_window

    if window is None:
        return False

    window_start, window_end = window
    candidates = generate_slot_candidates(
        window_start,
        window_end,
        service_duration_minutes,
    )

    start_time = scheduled_start.time()
    end_time = scheduled_end.time()
    aligned = any(
        candidate_start == start_time and candidate_end == end_time
        for candidate_start, candidate_end in candidates
    )
    if not aligned:
        return False

    return is_slot_available(scheduled_start, scheduled_end, blocking)
