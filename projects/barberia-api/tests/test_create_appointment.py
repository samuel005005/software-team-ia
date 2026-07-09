import uuid
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import delete, text

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

TZ = ZoneInfo("America/Santo_Domingo")


def _apply_exclusion_constraint(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist"))
        conn.execute(
            text(
                """
                ALTER TABLE appointments
                ADD CONSTRAINT ex_appointments_barber_no_overlap
                EXCLUDE USING gist (
                    barber_user_id WITH =,
                    tstzrange(scheduled_start, scheduled_end, '[)') WITH &&
                )
                WHERE (status NOT IN ('cancelada'))
                """
            )
        )


def _create_service(
    db_session,
    *,
    name: str = "Corte",
    duration_minutes: int = 30,
    is_active: bool = True,
) -> Service:
    service = Service(
        name=name,
        duration_minutes=duration_minutes,
        price_dop=Decimal("350.00"),
        is_active=is_active,
    )
    db_session.add(service)
    db_session.commit()
    return service


def _create_barber(
    db_session,
    *,
    display_name: str = "Carlos",
    is_bookable: bool = True,
    is_active: bool = True,
) -> User:
    user = User(
        email=f"barber-{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.BARBER,
        is_active=is_active,
    )
    user.barber_profile = BarberProfile(display_name=display_name, is_bookable=is_bookable)
    db_session.add(user)
    db_session.commit()
    return user


def _create_client(db_session) -> User:
    user = User(
        email=f"client-{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.CLIENT,
        is_active=True,
    )
    user.client_profile = ClientProfile(full_name="Cliente Test", phone="8090000000")
    db_session.add(user)
    db_session.commit()
    return user


def _assign_service(db_session, barber: User, service: Service) -> None:
    db_session.add(BarberService(barber_user_id=barber.id, service_id=service.id))
    db_session.commit()


def _set_barber_availability(
    db_session,
    barber: User,
    *,
    weekday: int,
    start_time: time = time(9, 0),
    end_time: time = time(17, 0),
) -> None:
    db_session.add(
        BarberAvailability(
            barber_user_id=barber.id,
            weekday=weekday,
            start_time=start_time,
            end_time=end_time,
            is_active=True,
        )
    )
    db_session.commit()


def _set_business_hours(
    db_session,
    *,
    weekday: int,
    open_time: time = time(8, 0),
    close_time: time = time(20, 0),
) -> None:
    db_session.add(
        BusinessHours(
            weekday=weekday,
            open_time=open_time,
            close_time=close_time,
            is_closed=False,
        )
    )
    db_session.commit()


def _next_weekday(target_weekday: int) -> date:
    today = date.today()
    days_ahead = (target_weekday - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)


def _register_and_login(client, db_session) -> tuple[str, User]:
    user = _create_client(db_session)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "password123"},
    )
    return login.json()["access_token"], user


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _seed_booking_context(db_session) -> tuple[Service, User, date, time]:
    service = _create_service(db_session)
    barber = _create_barber(db_session)
    _assign_service(db_session, barber, service)

    target_date = _next_weekday(0)
    weekday = target_date.weekday() + 1
    _set_barber_availability(db_session, barber, weekday=weekday)
    _set_business_hours(db_session, weekday=weekday)

    return service, barber, target_date, time(10, 0)


def _create_appointment(
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


@requires_db
def test_create_appointment_success(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, target_date, start_time = _seed_booking_context(db_session)
    token, _ = _register_and_login(client, db_session)

    scheduled_start = datetime.combine(target_date, start_time, tzinfo=TZ)
    response = client.post(
        "/api/v1/appointments",
        headers=_auth(token),
        json={
            "barber_user_id": str(barber.id),
            "service_id": str(service.id),
            "scheduled_start": scheduled_start.isoformat(),
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "confirmada"
    assert body["service_name"] == "Corte"
    assert body["barber_display_name"] == "Carlos"
    assert body["service_id"] == str(service.id)
    assert body["barber_user_id"] == str(barber.id)
    assert body["scheduled_start"] is not None
    assert body["scheduled_end"] is not None


@requires_db
def test_create_appointment_rejects_past(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, _, _ = _seed_booking_context(db_session)
    token, _ = _register_and_login(client, db_session)

    past_start = datetime.now(TZ) - timedelta(hours=1)
    response = client.post(
        "/api/v1/appointments",
        headers=_auth(token),
        json={
            "barber_user_id": str(barber.id),
            "service_id": str(service.id),
            "scheduled_start": past_start.isoformat(),
        },
    )

    assert response.status_code == 400
    assert "pasado" in response.json()["detail"].lower()


@requires_db
def test_create_appointment_rejects_occupied_slot(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, target_date, start_time = _seed_booking_context(db_session)
    existing_client = _create_client(db_session)
    _create_appointment(
        db_session,
        client=existing_client,
        barber=barber,
        service=service,
        target_date=target_date,
        start_time=start_time,
    )

    token, _ = _register_and_login(client, db_session)
    scheduled_start = datetime.combine(target_date, start_time, tzinfo=TZ)
    response = client.post(
        "/api/v1/appointments",
        headers=_auth(token),
        json={
            "barber_user_id": str(barber.id),
            "service_id": str(service.id),
            "scheduled_start": scheduled_start.isoformat(),
        },
    )

    assert response.status_code == 409


@requires_db
def test_create_appointment_rejects_inactive_service(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, target_date, start_time = _seed_booking_context(db_session)
    service.is_active = False
    db_session.commit()

    token, _ = _register_and_login(client, db_session)
    scheduled_start = datetime.combine(target_date, start_time, tzinfo=TZ)
    response = client.post(
        "/api/v1/appointments",
        headers=_auth(token),
        json={
            "barber_user_id": str(barber.id),
            "service_id": str(service.id),
            "scheduled_start": scheduled_start.isoformat(),
        },
    )

    assert response.status_code == 404
    assert "servicio" in response.json()["detail"].lower()


@requires_db
def test_create_appointment_rejects_unassigned_barber(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, target_date, start_time = _seed_booking_context(db_session)
    db_session.execute(
        delete(BarberService).where(
            BarberService.barber_user_id == barber.id,
            BarberService.service_id == service.id,
        )
    )
    db_session.commit()

    token, _ = _register_and_login(client, db_session)
    scheduled_start = datetime.combine(target_date, start_time, tzinfo=TZ)
    response = client.post(
        "/api/v1/appointments",
        headers=_auth(token),
        json={
            "barber_user_id": str(barber.id),
            "service_id": str(service.id),
            "scheduled_start": scheduled_start.isoformat(),
        },
    )

    assert response.status_code == 404
    assert "barbero" in response.json()["detail"].lower()


@requires_db
def test_create_appointment_rejects_outside_availability(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, target_date, _ = _seed_booking_context(db_session)
    token, _ = _register_and_login(client, db_session)

    scheduled_start = datetime.combine(target_date, time(7, 0), tzinfo=TZ)
    response = client.post(
        "/api/v1/appointments",
        headers=_auth(token),
        json={
            "barber_user_id": str(barber.id),
            "service_id": str(service.id),
            "scheduled_start": scheduled_start.isoformat(),
        },
    )

    assert response.status_code == 409


@requires_db
def test_create_appointment_rejects_non_bookable_barber(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, target_date, start_time = _seed_booking_context(db_session)
    barber.barber_profile.is_bookable = False
    db_session.commit()

    token, _ = _register_and_login(client, db_session)
    scheduled_start = datetime.combine(target_date, start_time, tzinfo=TZ)
    response = client.post(
        "/api/v1/appointments",
        headers=_auth(token),
        json={
            "barber_user_id": str(barber.id),
            "service_id": str(service.id),
            "scheduled_start": scheduled_start.isoformat(),
        },
    )

    assert response.status_code == 404
