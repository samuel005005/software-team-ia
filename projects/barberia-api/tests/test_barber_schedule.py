import uuid
from datetime import date, datetime, time, timedelta

from app.domain.appointments.scheduling import calculate_scheduled_end
from app.domain.enums import AppointmentStatus, UserRole
from app.infrastructure.db.models.appointment import Appointment
from app.infrastructure.db.models.barber_profile import BarberProfile
from app.infrastructure.db.models.client_profile import ClientProfile
from app.infrastructure.db.models.user import User
from app.infrastructure.security.password_hasher import hash_password
from tests.conftest import requires_db
from tests.test_create_appointment import (
    TZ,
    _apply_exclusion_constraint,
    _assign_service,
    _auth,
    _create_barber,
    _create_client,
    _create_service,
    _register_and_login,
)


def _login_barber(client, db_session, *, barber: User | None = None) -> tuple[str, User]:
    if barber is None:
        barber = _create_barber(db_session)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": barber.email, "password": "password123"},
    )
    return login.json()["access_token"], barber


def _create_user_and_login(
    client,
    db_session,
    *,
    role: UserRole,
) -> tuple[str, User]:
    user = User(
        email=f"{role.value}-{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("password123"),
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
        json={"email": user.email, "password": "password123"},
    )
    return login.json()["access_token"], user


def _create_appointment(
    db_session,
    *,
    client: User,
    barber: User,
    service,
    target_date: date,
    start_time: time,
    status: AppointmentStatus = AppointmentStatus.CONFIRMADA,
) -> Appointment:
    start = datetime.combine(target_date, start_time, tzinfo=TZ)
    appointment = Appointment(
        client_user_id=client.id,
        barber_user_id=barber.id,
        service_id=service.id,
        scheduled_start=start,
        scheduled_end=calculate_scheduled_end(start, service.duration_minutes),
        status=status,
    )
    db_session.add(appointment)
    db_session.commit()
    return appointment


def _seed_barber_with_client(
    db_session,
    *,
    client_name: str = "Juan Pérez",
) -> tuple:
    service = _create_service(db_session, name="Corte")
    barber = _create_barber(db_session, display_name="Carlos")
    _assign_service(db_session, barber, service)
    client = _create_client(db_session)
    client.client_profile.full_name = client_name
    db_session.commit()
    return service, barber, client


@requires_db
def test_barber_schedule_requires_auth(client) -> None:
    response = client.get("/api/v1/barber/schedule")
    assert response.status_code == 401


@requires_db
def test_barber_schedule_rejects_client(client, db_session) -> None:
    token, _ = _register_and_login(client, db_session)
    response = client.get("/api/v1/barber/schedule", headers=_auth(token))
    assert response.status_code == 403


@requires_db
def test_barber_schedule_rejects_admin(client, db_session) -> None:
    token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    response = client.get("/api/v1/barber/schedule", headers=_auth(token))
    assert response.status_code == 403


@requires_db
def test_barber_schedule_empty_day(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    barber = _create_barber(db_session)
    token, _ = _login_barber(client, db_session, barber=barber)

    response = client.get(
        "/api/v1/barber/schedule",
        params={"date": "2030-01-15"},
        headers=_auth(token),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["from_date"] == "2030-01-15"
    assert body["to_date"] == "2030-01-15"
    assert body["items"] == []


@requires_db
def test_barber_schedule_returns_fields(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    target_date = date(2030, 3, 4)
    _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=target_date,
        start_time=time(10, 0),
    )

    token, _ = _login_barber(client, db_session, barber=barber)
    response = client.get(
        "/api/v1/barber/schedule",
        params={"date": target_date.isoformat()},
        headers=_auth(token),
    )

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["status"] == "confirmada"
    assert item["service_name"] == "Corte"
    assert item["client_display_name"] == "Juan Pérez"
    assert item["scheduled_start"] is not None
    assert item["scheduled_end"] is not None
    assert item["service_id"] == str(service.id)
    assert item["client_user_id"] == str(client_user.id)


@requires_db
def test_barber_schedule_chronological_order(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    target_date = date(2030, 3, 5)

    _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=target_date,
        start_time=time(14, 0),
    )
    _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=target_date,
        start_time=time(10, 0),
    )

    token, _ = _login_barber(client, db_session, barber=barber)
    response = client.get(
        "/api/v1/barber/schedule",
        params={"date": target_date.isoformat()},
        headers=_auth(token),
    )

    starts = [item["scheduled_start"] for item in response.json()["items"]]
    assert starts == sorted(starts)
    assert len(starts) == 2


@requires_db
def test_barber_schedule_isolation(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber_a, client_user = _seed_barber_with_client(db_session)
    barber_b = _create_barber(db_session, display_name="Otro Barbero")
    target_date = date(2030, 3, 6)

    _create_appointment(
        db_session,
        client=client_user,
        barber=barber_a,
        service=service,
        target_date=target_date,
        start_time=time(10, 0),
    )

    token, _ = _login_barber(client, db_session, barber=barber_b)
    response = client.get(
        "/api/v1/barber/schedule",
        params={"date": target_date.isoformat()},
        headers=_auth(token),
    )

    assert response.status_code == 200
    assert response.json()["items"] == []


@requires_db
def test_barber_schedule_filters_by_date(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    day_x = date(2030, 4, 1)
    day_y = date(2030, 4, 2)

    _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=day_x,
        start_time=time(10, 0),
    )

    token, _ = _login_barber(client, db_session, barber=barber)
    response = client.get(
        "/api/v1/barber/schedule",
        params={"date": day_y.isoformat()},
        headers=_auth(token),
    )

    assert response.status_code == 200
    assert response.json()["items"] == []


@requires_db
def test_barber_schedule_includes_cancelled(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    target_date = date(2030, 4, 10)

    _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=target_date,
        start_time=time(11, 0),
        status=AppointmentStatus.CANCELADA,
    )

    token, _ = _login_barber(client, db_session, barber=barber)
    response = client.get(
        "/api/v1/barber/schedule",
        params={"date": target_date.isoformat()},
        headers=_auth(token),
    )

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["status"] == "cancelada"


@requires_db
def test_barber_schedule_week_range(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    day_one = date(2030, 5, 1)
    day_three = date(2030, 5, 3)

    _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=day_one,
        start_time=time(9, 0),
    )
    _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=day_three,
        start_time=time(15, 0),
    )

    token, _ = _login_barber(client, db_session, barber=barber)
    response = client.get(
        "/api/v1/barber/schedule",
        params={"date": day_one.isoformat(), "end_date": "2030-05-07"},
        headers=_auth(token),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["from_date"] == "2030-05-01"
    assert body["to_date"] == "2030-05-07"
    assert len(body["items"]) == 2
    starts = [item["scheduled_start"] for item in body["items"]]
    assert starts == sorted(starts)


@requires_db
def test_barber_schedule_rejects_invalid_range(client, db_session) -> None:
    token, _ = _login_barber(client, db_session)
    response = client.get(
        "/api/v1/barber/schedule",
        params={"date": "2030-06-10", "end_date": "2030-06-09"},
        headers=_auth(token),
    )
    assert response.status_code == 400


@requires_db
def test_barber_schedule_rejects_range_over_7_days(client, db_session) -> None:
    token, _ = _login_barber(client, db_session)
    response = client.get(
        "/api/v1/barber/schedule",
        params={"date": "2030-06-01", "end_date": "2030-06-09"},
        headers=_auth(token),
    )
    assert response.status_code == 400


@requires_db
def test_barber_schedule_default_date_is_today(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    today = datetime.now(TZ).date()

    _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=today,
        start_time=time(12, 0),
    )

    token, _ = _login_barber(client, db_session, barber=barber)
    response = client.get("/api/v1/barber/schedule", headers=_auth(token))

    assert response.status_code == 200
    body = response.json()
    assert body["from_date"] == today.isoformat()
    assert body["to_date"] == today.isoformat()
    assert len(body["items"]) == 1
