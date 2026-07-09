import uuid
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.domain.appointments.scheduling import calculate_scheduled_end
from app.domain.enums import AppointmentStatus, UserRole
from app.infrastructure.db.models.appointment import Appointment
from app.infrastructure.db.models.barber_profile import BarberProfile
from app.infrastructure.db.models.barber_service import BarberService
from app.infrastructure.db.models.client_profile import ClientProfile
from app.infrastructure.db.models.schedule import BarberAvailability, BusinessHours
from app.infrastructure.db.models.service import Service
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
    _next_weekday,
    _register_and_login,
    _set_barber_availability,
    _set_business_hours,
)


def _create_appointment_for_client(
    db_session,
    *,
    client: User,
    barber: User,
    service: Service,
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


def _seed_context(db_session) -> tuple[Service, User]:
    service = _create_service(db_session, name="Corte")
    barber = _create_barber(db_session, display_name="Carlos")
    _assign_service(db_session, barber, service)

    target_date = _next_weekday(0)
    weekday = target_date.weekday() + 1
    _set_barber_availability(db_session, barber, weekday=weekday)
    _set_business_hours(db_session, weekday=weekday)

    return service, barber


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


@requires_db
def test_list_my_appointments_requires_auth(client) -> None:
    response = client.get("/api/v1/appointments")
    assert response.status_code == 401


@requires_db
def test_list_my_appointments_requires_client(client, db_session) -> None:
    for role in (UserRole.BARBER, UserRole.ADMIN):
        token, _ = _create_user_and_login(client, db_session, role=role)
        response = client.get("/api/v1/appointments", headers=_auth(token))
        assert response.status_code == 403


@requires_db
def test_list_my_appointments_empty(client, db_session) -> None:
    token, _ = _register_and_login(client, db_session)
    response = client.get("/api/v1/appointments", headers=_auth(token))
    assert response.status_code == 200
    assert response.json() == {"items": []}


@requires_db
def test_list_my_appointments_returns_own_only(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber = _seed_context(db_session)
    token_a, client_a = _register_and_login(client, db_session)
    client_b = _create_client(db_session)

    future_date = _next_weekday(1)
    _create_appointment_for_client(
        db_session,
        client=client_a,
        barber=barber,
        service=service,
        target_date=future_date,
        start_time=time(10, 0),
    )
    _create_appointment_for_client(
        db_session,
        client=client_b,
        barber=barber,
        service=service,
        target_date=future_date,
        start_time=time(11, 0),
    )

    response = client.get("/api/v1/appointments", headers=_auth(token_a))
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["service_name"] == "Corte"
    assert items[0]["barber_display_name"] == "Carlos"


@requires_db
def test_list_my_appointments_fields(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber = _seed_context(db_session)
    token, user = _register_and_login(client, db_session)

    future_date = _next_weekday(2)
    _create_appointment_for_client(
        db_session,
        client=user,
        barber=barber,
        service=service,
        target_date=future_date,
        start_time=time(14, 30),
        status=AppointmentStatus.CONFIRMADA,
    )

    response = client.get("/api/v1/appointments", headers=_auth(token))
    assert response.status_code == 200
    item = response.json()["items"][0]

    assert item["status"] == "confirmada"
    assert item["service_name"] == "Corte"
    assert item["barber_display_name"] == "Carlos"
    assert item["service_id"] == str(service.id)
    assert item["barber_user_id"] == str(barber.id)
    assert item["scheduled_start"] is not None
    assert item["scheduled_end"] is not None


@requires_db
def test_list_my_appointments_order_upcoming_first(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber = _seed_context(db_session)
    token, user = _register_and_login(client, db_session)

    past_date = date.today() - timedelta(days=14)
    future_date = _next_weekday(3)

    _create_appointment_for_client(
        db_session,
        client=user,
        barber=barber,
        service=service,
        target_date=past_date,
        start_time=time(9, 0),
        status=AppointmentStatus.COMPLETADA,
    )
    _create_appointment_for_client(
        db_session,
        client=user,
        barber=barber,
        service=service,
        target_date=future_date,
        start_time=time(10, 0),
    )

    response = client.get("/api/v1/appointments", headers=_auth(token))
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 2

    future_start = datetime.fromisoformat(items[0]["scheduled_start"])
    past_start = datetime.fromisoformat(items[1]["scheduled_start"])
    assert future_start > datetime.now(TZ)
    assert past_start < datetime.now(TZ)


@requires_db
def test_list_my_appointments_order_within_upcoming(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber = _seed_context(db_session)
    token, user = _register_and_login(client, db_session)

    nearer_date = _next_weekday(4)
    farther_date = nearer_date + timedelta(days=7)

    _create_appointment_for_client(
        db_session,
        client=user,
        barber=barber,
        service=service,
        target_date=farther_date,
        start_time=time(10, 0),
    )
    _create_appointment_for_client(
        db_session,
        client=user,
        barber=barber,
        service=service,
        target_date=nearer_date,
        start_time=time(11, 0),
    )

    response = client.get("/api/v1/appointments", headers=_auth(token))
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 2

    first_start = datetime.fromisoformat(items[0]["scheduled_start"])
    second_start = datetime.fromisoformat(items[1]["scheduled_start"])
    assert first_start < second_start
