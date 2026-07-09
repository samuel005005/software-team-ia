from datetime import time

from app.domain.enums import UserRole
from app.infrastructure.db.models.schedule import BusinessHours
from tests.conftest import requires_db
from tests.test_role_guards import _auth, _create_user_and_login


def _week_payload(
    *,
    weekday: int,
    open_time: str = "09:00:00",
    close_time: str = "18:00:00",
    is_closed: bool = False,
) -> dict:
    return {
        "weekday": weekday,
        "open_time": open_time,
        "close_time": close_time,
        "is_closed": is_closed,
    }


def _full_week_payload(**overrides: dict) -> dict:
    items = [_week_payload(weekday=day) for day in range(1, 8)]
    for index, item in enumerate(items):
        weekday = item["weekday"]
        if weekday in overrides:
            item.update(overrides[weekday])
    return {"items": items}


@requires_db
def test_admin_list_business_hours_empty(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)

    response = client.get("/api/v1/admin/business-hours", headers=_auth(admin_token))

    assert response.status_code == 200
    assert response.json()["items"] == []


@requires_db
def test_admin_update_business_hours_replaces_week(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    db_session.add(
        BusinessHours(
            weekday=1,
            open_time=time(8, 0),
            close_time=time(12, 0),
            is_closed=False,
        )
    )
    db_session.commit()

    payload = _full_week_payload()
    for item in payload["items"]:
        if item["weekday"] == 1:
            item.update({"open_time": "10:00:00", "close_time": "19:00:00"})
        if item["weekday"] == 7:
            item["is_closed"] = True

    response = client.patch(
        "/api/v1/admin/business-hours",
        headers=_auth(admin_token),
        json=payload,
    )

    assert response.status_code == 200
    body = response.json()["items"]
    assert len(body) == 7
    monday = next(item for item in body if item["weekday"] == 1)
    sunday = next(item for item in body if item["weekday"] == 7)
    assert monday["open_time"] == "10:00:00"
    assert monday["close_time"] == "19:00:00"
    assert sunday["is_closed"] is True

    listed = client.get("/api/v1/admin/business-hours", headers=_auth(admin_token))
    assert len(listed.json()["items"]) == 7


@requires_db
def test_admin_update_business_hours_rejects_invalid_range(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)

    response = client.patch(
        "/api/v1/admin/business-hours",
        headers=_auth(admin_token),
        json={
            "items": [
                _week_payload(
                    weekday=2,
                    open_time="18:00:00",
                    close_time="09:00:00",
                )
            ]
        },
    )

    assert response.status_code == 400
    assert "apertura" in response.json()["detail"].lower()


@requires_db
def test_admin_update_business_hours_rejects_duplicate_weekday(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)

    response = client.patch(
        "/api/v1/admin/business-hours",
        headers=_auth(admin_token),
        json={
            "items": [
                _week_payload(weekday=3),
                _week_payload(weekday=3, close_time="20:00:00"),
            ]
        },
    )

    assert response.status_code == 422


@requires_db
def test_admin_business_hours_forbidden_for_client(client, db_session) -> None:
    client_token, _ = _create_user_and_login(client, db_session, role=UserRole.CLIENT)

    response = client.get("/api/v1/admin/business-hours", headers=_auth(client_token))

    assert response.status_code == 403
