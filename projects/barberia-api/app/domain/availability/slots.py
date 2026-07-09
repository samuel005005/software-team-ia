from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.domain.availability.constants import SLOT_STEP_MINUTES


@dataclass(frozen=True)
class TimeSlot:
    start: datetime
    end: datetime


@dataclass(frozen=True)
class BlockingInterval:
    start: datetime
    end: datetime


def intersect_time_windows(
    a_start: time,
    a_end: time,
    b_start: time,
    b_end: time,
) -> tuple[time, time] | None:
    start = max(a_start, b_start)
    end = min(a_end, b_end)
    return (start, end) if start < end else None


def _add_minutes_to_time(value: time, minutes: int) -> time:
    combined = datetime.combine(date.min, value) + timedelta(minutes=minutes)
    return combined.time()


def generate_slot_candidates(
    window_start: time,
    window_end: time,
    duration_minutes: int,
) -> list[tuple[time, time]]:
    if duration_minutes <= 0:
        return []

    slots: list[tuple[time, time]] = []
    cursor = window_start
    while True:
        slot_end = _add_minutes_to_time(cursor, duration_minutes)
        if slot_end > window_end:
            break
        slots.append((cursor, slot_end))
        cursor = _add_minutes_to_time(cursor, SLOT_STEP_MINUTES)
    return slots


def intervals_overlap(
    slot_start: datetime,
    slot_end: datetime,
    block_start: datetime,
    block_end: datetime,
) -> bool:
    return slot_start < block_end and slot_end > block_start


def is_slot_available(
    slot_start: datetime,
    slot_end: datetime,
    blocking: list[BlockingInterval],
) -> bool:
    return not any(
        intervals_overlap(slot_start, slot_end, interval.start, interval.end)
        for interval in blocking
    )


def filter_available_slots(
    candidates: list[tuple[time, time]],
    blocking: list[BlockingInterval],
    now: datetime,
    target_date: date,
    tz: ZoneInfo,
) -> list[TimeSlot]:
    result: list[TimeSlot] = []
    for start_time, end_time in candidates:
        start_dt = datetime.combine(target_date, start_time, tzinfo=tz)
        end_dt = datetime.combine(target_date, end_time, tzinfo=tz)
        if target_date == now.date() and start_dt <= now:
            continue
        if not is_slot_available(start_dt, end_dt, blocking):
            continue
        result.append(TimeSlot(start=start_dt, end=end_dt))
    return result
