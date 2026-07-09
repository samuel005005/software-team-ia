from datetime import time

from app.domain.enums import UserRole
from app.infrastructure.db.models.schedule import BarberAvailability
from app.infrastructure.db.models.user import User
from tests.conftest import requires_db
from tests.test_role_guards import _auth, _create_user_and_login


def _day_payload(
    *,
    weekday: int,
    start_time: str = "09:00:00",
    end_time: str = "18:00:00",
    is_active: bool = True,
) -> dict:
    return {
        "weekday": weekday,
        "start_time": start_time,
        "end_time": end_time,
        "is_active": is_active,
    }


def _full_week_payload(**overrides: dict) -> dict:
    items = [_day_payload(weekday=day) for day in range(1, 8)]
    for item in items:
        weekday = item["weekday"]
        if weekday in overrides:
            item.update(overrides[weekday])
    return {"items": items}


@requires_db
def test_barber_list_availability_empty(client, db_session) -> None:
    barber_token, _ = _create_user_and_login(
        client, db_session, role=UserRole.BARBER
    )

    response = client.get("/api/v1/barber/availability", headers=_auth(barber_token))

    assert response.status_code == 200
    assert response.json()["items"] == []


@requires_db
def test_barber_update_availability_replaces_week(client, db_session) -> None:
    barber_token, barber_email = _create_user_and_login(
        client, db_session, role=UserRole.BARBER
    )
    barber = db_session.query(User).filter_by(email=barber_email).one()

    db_session.add(
        BarberAvailability(
            barber_user_id=barber.id,
            weekday=1,
            start_time=time(8, 0),
            end_time=time(12, 0),
            is_active=True,
        )
    )
    db_session.commit()

    payload = _full_week_payload()
    for item in payload["items"]:
        if item["weekday"] == 1:
            item.update({"start_time": "10:00:00", "end_time": "19:00:00"})
        if item["weekday"] == 7:
            item["is_active"] = False

    response = client.patch(
        "/api/v1/barber/availability",
        headers=_auth(barber_token),
        json=payload,
    )

    assert response.status_code == 200
    body = response.json()["items"]
    assert len(body) == 7
    monday = next(item for item in body if item["weekday"] == 1)
    sunday = next(item for item in body if item["weekday"] == 7)
    assert monday["start_time"] == "10:00:00"
    assert monday["end_time"] == "19:00:00"
    assert sunday["is_active"] is False

    listed = client.get("/api/v1/barber/availability", headers=_auth(barber_token))
    assert len(listed.json()["items"]) == 7


@requires_db
def test_barber_update_availability_rejects_invalid_range(client, db_session) -> None:
    barber_token, _ = _create_user_and_login(
        client, db_session, role=UserRole.BARBER
    )

    response = client.patch(
        "/api/v1/barber/availability",
        headers=_auth(barber_token),
        json={
            "items": [
                _day_payload(
                    weekday=2,
                    start_time="18:00:00",
                    end_time="09:00:00",
                )
            ]
        },
    )

    assert response.status_code == 400


@requires_db
def test_barber_update_availability_rejects_duplicate_weekdays(
    client, db_session
) -> None:
    barber_token, _ = _create_user_and_login(
        client, db_session, role=UserRole.BARBER
    )

    response = client.patch(
        "/api/v1/barber/availability",
        headers=_auth(barber_token),
        json={
            "items": [
                _day_payload(weekday=3),
                _day_payload(weekday=3, start_time="14:00:00"),
            ]
        },
    )

    assert response.status_code == 422


@requires_db
def test_barber_availability_forbidden_for_client(client) -> None:
    from tests.test_role_guards import _register_client

    token, _ = _register_client(client)

    assert (
        client.get("/api/v1/barber/availability", headers=_auth(token)).status_code
        == 403
    )
    assert (
        client.patch(
            "/api/v1/barber/availability",
            headers=_auth(token),
            json={"items": [_day_payload(weekday=1)]},
        ).status_code
        == 403
    )


@requires_db
def test_barber_availability_isolated_per_barber(client, db_session) -> None:
    barber_a_token, _ = _create_user_and_login(
        client, db_session, role=UserRole.BARBER
    )
    barber_b_token, _ = _create_user_and_login(
        client, db_session, role=UserRole.BARBER
    )

    client.patch(
        "/api/v1/barber/availability",
        headers=_auth(barber_a_token),
        json={"items": [_day_payload(weekday=1, start_time="08:00:00")]},
    )

    response = client.get("/api/v1/barber/availability", headers=_auth(barber_b_token))
    assert response.status_code == 200
    assert response.json()["items"] == []
