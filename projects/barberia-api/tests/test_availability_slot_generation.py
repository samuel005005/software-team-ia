from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest

from app.domain.availability.slots import (
    BlockingInterval,
    filter_available_slots,
    generate_slot_candidates,
    intersect_time_windows,
    intervals_overlap,
    is_slot_available,
)

TZ = ZoneInfo("America/Santo_Domingo")


def test_intersect_time_windows_with_overlap() -> None:
    result = intersect_time_windows(
        time(9, 0),
        time(17, 0),
        time(10, 0),
        time(18, 0),
    )
    assert result == (time(10, 0), time(17, 0))


def test_intersect_time_windows_without_overlap() -> None:
    assert intersect_time_windows(time(9, 0), time(12, 0), time(13, 0), time(17, 0)) is None


def test_generate_slot_candidates_30_minutes() -> None:
    slots = generate_slot_candidates(time(9, 0), time(17, 0), 30)
    assert slots[0] == (time(9, 0), time(9, 30))
    assert slots[1] == (time(9, 15), time(9, 45))
    assert slots[-1] == (time(16, 30), time(17, 0))
    assert len(slots) == 31


def test_generate_slot_candidates_60_minutes_short_window() -> None:
    slots = generate_slot_candidates(time(9, 0), time(10, 30), 60)
    assert slots == [
        (time(9, 0), time(10, 0)),
        (time(9, 15), time(10, 15)),
        (time(9, 30), time(10, 30)),
    ]


def test_generate_slot_candidates_window_too_short() -> None:
    assert generate_slot_candidates(time(9, 0), time(9, 20), 30) == []


def test_intervals_overlap_detects_partial_overlap() -> None:
    start = datetime(2026, 7, 10, 10, 0, tzinfo=TZ)
    end = datetime(2026, 7, 10, 10, 30, tzinfo=TZ)
    block_start = datetime(2026, 7, 10, 10, 15, tzinfo=TZ)
    block_end = datetime(2026, 7, 10, 11, 0, tzinfo=TZ)
    assert intervals_overlap(start, end, block_start, block_end) is True


def test_is_slot_available_without_blocking() -> None:
    start = datetime(2026, 7, 10, 10, 0, tzinfo=TZ)
    end = datetime(2026, 7, 10, 10, 30, tzinfo=TZ)
    assert is_slot_available(start, end, []) is True


def test_is_slot_available_rejects_overlap() -> None:
    start = datetime(2026, 7, 10, 10, 0, tzinfo=TZ)
    end = datetime(2026, 7, 10, 10, 30, tzinfo=TZ)
    blocking = [
        BlockingInterval(
            start=datetime(2026, 7, 10, 10, 0, tzinfo=TZ),
            end=datetime(2026, 7, 10, 10, 30, tzinfo=TZ),
        )
    ]
    assert is_slot_available(start, end, blocking) is False


def test_filter_available_slots_excludes_past_slots_for_today() -> None:
    target_date = date(2026, 7, 10)
    now = datetime(2026, 7, 10, 14, 0, tzinfo=TZ)
    candidates = [
        (time(13, 0), time(13, 30)),
        (time(14, 0), time(14, 30)),
        (time(14, 15), time(14, 45)),
    ]

    available = filter_available_slots(candidates, [], now, target_date, TZ)

    assert len(available) == 1
    assert available[0].start == datetime(2026, 7, 10, 14, 15, tzinfo=TZ)


def test_filter_available_slots_excludes_blocking_appointment() -> None:
    target_date = date(2026, 7, 10)
    now = datetime(2026, 7, 9, 12, 0, tzinfo=TZ)
    candidates = [
        (time(10, 0), time(10, 30)),
        (time(10, 30), time(11, 0)),
    ]
    blocking = [
        BlockingInterval(
            start=datetime(2026, 7, 10, 10, 0, tzinfo=TZ),
            end=datetime(2026, 7, 10, 10, 30, tzinfo=TZ),
        )
    ]

    available = filter_available_slots(candidates, blocking, now, target_date, TZ)

    assert len(available) == 1
    assert available[0].start == datetime(2026, 7, 10, 10, 30, tzinfo=TZ)


def test_generate_slot_candidates_rejects_invalid_duration() -> None:
    assert generate_slot_candidates(time(9, 0), time(17, 0), 0) == []


@pytest.mark.parametrize(
    ("duration", "expected_count"),
    [
        (30, 31),
        (45, 30),
        (60, 29),
    ],
)
def test_generate_slot_candidates_respects_service_duration(
    duration: int,
    expected_count: int,
) -> None:
    slots = generate_slot_candidates(time(9, 0), time(17, 0), duration)
    assert len(slots) == expected_count
