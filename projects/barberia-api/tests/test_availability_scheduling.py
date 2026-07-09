from datetime import date

import pytest

from app.domain.availability.scheduling import date_to_weekday


@pytest.mark.parametrize(
    ("target_date", "expected"),
    [
        (date(2026, 7, 6), 1),  # Monday
        (date(2026, 7, 7), 2),  # Tuesday
        (date(2026, 7, 12), 7),  # Sunday
    ],
)
def test_date_to_weekday_maps_python_weekday_to_domain(target_date: date, expected: int) -> None:
    assert date_to_weekday(target_date) == expected
