import uuid

import pytest
from fastapi.testclient import TestClient

from app.domain.enums import UserRole
from app.infrastructure.db.models.barber_profile import BarberProfile
from app.infrastructure.db.models.client_profile import ClientProfile
from app.infrastructure.db.models.user import User
from app.infrastructure.security.password_hasher import hash_password
from tests.conftest import requires_db


def _register_client(client) -> tuple[str, str]:
    email = f"client-{uuid.uuid4().hex[:8]}@test.com"
    password = "password123"
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Cliente Test",
            "phone": "8095551111",
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return login.json()["access_token"], email


def _create_user_and_login(
    client,
    db_session,
    *,
    role: UserRole,
    email: str | None = None,
) -> tuple[str, str]:
    addr = email or f"{role.value}-{uuid.uuid4().hex[:8]}@test.com"
    password = "password123"
    user = User(
        email=addr,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
    )
    if role == UserRole.CLIENT:
        user.client_profile = ClientProfile(
            full_name="Cliente Test",
            phone="8095551111",
        )
    elif role == UserRole.BARBER:
        user.barber_profile = BarberProfile(
            display_name="Barbero Test",
            is_bookable=True,
        )
    db_session.add(user)
    db_session.commit()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": addr, "password": password},
    )
    return login.json()["access_token"], addr


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@requires_db
def test_admin_routes_require_authentication(client) -> None:
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 401


@requires_db
def test_admin_routes_reject_client(client, db_session) -> None:
    token, _ = _register_client(client)
    response = client.get("/api/v1/admin/users", headers=_auth(token))
    assert response.status_code == 403


@requires_db
def test_admin_routes_reject_barber(client, db_session) -> None:
    token, _ = _create_user_and_login(client, db_session, role=UserRole.BARBER)
    response = client.get("/api/v1/admin/services", headers=_auth(token))
    assert response.status_code == 403


@requires_db
def test_admin_routes_allow_admin(client, db_session) -> None:
    token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    response = client.get("/api/v1/admin/services", headers=_auth(token))
    assert response.status_code == 200
    response = client.get("/api/v1/admin/barbers", headers=_auth(token))
    assert response.status_code == 200


@requires_db
def test_appointments_create_requires_client(client, db_session) -> None:
    barber_token, _ = _create_user_and_login(client, db_session, role=UserRole.BARBER)
    response = client.post(
        "/api/v1/appointments",
        headers=_auth(barber_token),
        json={
            "service_id": "00000000-0000-0000-0000-000000000001",
            "barber_user_id": "00000000-0000-0000-0000-000000000002",
            "scheduled_start": "2026-07-10T10:00:00",
        },
    )
    assert response.status_code == 403


@requires_db
def test_appointments_create_allows_client(client, db_session) -> None:
    from datetime import date, datetime, time, timedelta
    from decimal import Decimal
    from zoneinfo import ZoneInfo

    from app.infrastructure.db.models.barber_profile import BarberProfile
    from app.infrastructure.db.models.barber_service import BarberService
    from app.infrastructure.db.models.schedule import BarberAvailability, BusinessHours
    from app.infrastructure.db.models.service import Service
    from app.infrastructure.db.models.user import User
    from app.infrastructure.security.password_hasher import hash_password

    tz = ZoneInfo("America/Santo_Domingo")
    service = Service(
        name="Corte",
        duration_minutes=30,
        price_dop=Decimal("350.00"),
        is_active=True,
    )
    barber = User(
        email=f"barber-{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.BARBER,
        is_active=True,
    )
    barber.barber_profile = BarberProfile(display_name="Carlos", is_bookable=True)
    db_session.add_all([service, barber])
    db_session.commit()

    db_session.add(BarberService(barber_user_id=barber.id, service_id=service.id))
    target_date = date.today() + timedelta(days=7)
    weekday = target_date.weekday() + 1
    db_session.add(
        BarberAvailability(
            barber_user_id=barber.id,
            weekday=weekday,
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_active=True,
        )
    )
    db_session.add(
        BusinessHours(
            weekday=weekday,
            open_time=time(8, 0),
            close_time=time(20, 0),
            is_closed=False,
        )
    )
    db_session.commit()

    token, _ = _register_client(client)
    scheduled_start = datetime.combine(target_date, time(10, 0), tzinfo=tz)
    response = client.post(
        "/api/v1/appointments",
        headers=_auth(token),
        json={
            "service_id": str(service.id),
            "barber_user_id": str(barber.id),
            "scheduled_start": scheduled_start.isoformat(),
        },
    )
    assert response.status_code == 201
    assert response.json()["status"] == "confirmada"


@requires_db
def test_appointments_list_requires_authentication(client) -> None:
    response = client.get("/api/v1/appointments")
    assert response.status_code == 401


@requires_db
def test_appointments_list_allows_client(client, db_session) -> None:
    token, _ = _create_user_and_login(client, db_session, role=UserRole.CLIENT)
    response = client.get("/api/v1/appointments", headers=_auth(token))
    assert response.status_code == 200
    assert response.json() == {"items": []}


@requires_db
def test_appointments_list_rejects_non_client(client, db_session) -> None:
    for role in (UserRole.BARBER, UserRole.ADMIN):
        token, _ = _create_user_and_login(client, db_session, role=role)
        response = client.get("/api/v1/appointments", headers=_auth(token))
        assert response.status_code == 403


@requires_db
def test_appointments_cancel_requires_client(client, db_session) -> None:
    for role in (UserRole.BARBER, UserRole.ADMIN):
        token, _ = _create_user_and_login(client, db_session, role=role)
        response = client.patch(
            f"/api/v1/appointments/{uuid.uuid4()}/cancel",
            headers=_auth(token),
        )
        assert response.status_code == 403


@requires_db
def test_barber_routes_reject_client(client) -> None:
    token, _ = _register_client(client)
    response = client.patch(
        "/api/v1/barber/availability",
        headers=_auth(token),
        json={},
    )
    assert response.status_code == 403


@requires_db
def test_barber_routes_allow_barber(client, db_session) -> None:
    token, _ = _create_user_and_login(client, db_session, role=UserRole.BARBER)
    response = client.patch(
        "/api/v1/barber/availability",
        headers=_auth(token),
        json={"items": [{"weekday": 1, "start_time": "09:00:00", "end_time": "18:00:00", "is_active": True}]},
    )
    assert response.status_code == 200


@requires_db
def test_public_catalog_endpoints_remain_open(client) -> None:
    assert client.get("/api/v1/barbers").status_code == 200
    assert client.get("/api/v1/services").status_code == 200
