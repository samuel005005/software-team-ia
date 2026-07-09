import uuid
from datetime import date, datetime, time, timedelta
from decimal import Decimal
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

TZ = ZoneInfo("America/Santo_Domingo")


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
    display_name: str,
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
    is_active: bool = True,
) -> None:
    db_session.add(
        BarberAvailability(
            barber_user_id=barber.id,
            weekday=weekday,
            start_time=start_time,
            end_time=end_time,
            is_active=is_active,
        )
    )
    db_session.commit()


def _set_business_hours(
    db_session,
    *,
    weekday: int,
    open_time: time = time(8, 0),
    close_time: time = time(20, 0),
    is_closed: bool = False,
) -> None:
    db_session.add(
        BusinessHours(
            weekday=weekday,
            open_time=open_time,
            close_time=close_time,
            is_closed=is_closed,
        )
    )
    db_session.commit()


def _next_weekday(target_weekday: int) -> date:
    today = date.today()
    days_ahead = (target_weekday - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)


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
def test_availability_generates_slots_without_appointments(client, db_session) -> None:
    service = _create_service(db_session)
    barber = _create_barber(db_session, display_name="Ana")
    _assign_service(db_session, barber, service)
    target_date = _next_weekday(0)
    _set_barber_availability(db_session, barber, weekday=1)

    response = client.get(
        f"/api/v1/availability?service_id={service.id}&date={target_date.isoformat()}"
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["slots"]) == 31
    assert "T09:00:00" in body["slots"][0]["start"]
    assert "T16:30:00" in body["slots"][-1]["start"]
    assert all(slot["barber_user_id"] == str(barber.id) for slot in body["slots"])


@requires_db
def test_availability_excludes_slot_blocked_by_confirmed_appointment(client, db_session) -> None:
    service = _create_service(db_session)
    barber = _create_barber(db_session, display_name="Ana")
    client_user = _create_client(db_session)
    _assign_service(db_session, barber, service)
    target_date = _next_weekday(0)
    _set_barber_availability(db_session, barber, weekday=1)
    _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=target_date,
        start_time=time(10, 0),
    )

    response = client.get(
        f"/api/v1/availability?service_id={service.id}&date={target_date.isoformat()}"
    )

    assert response.status_code == 200
    starts = [slot["start"] for slot in response.json()["slots"]]
    assert not any("T10:00:00" in start for start in starts)
    assert any("T10:30:00" in start for start in starts)


@requires_db
def test_availability_allows_slot_when_appointment_is_cancelled(client, db_session) -> None:
    service = _create_service(db_session)
    barber = _create_barber(db_session, display_name="Ana")
    client_user = _create_client(db_session)
    _assign_service(db_session, barber, service)
    target_date = _next_weekday(0)
    _set_barber_availability(db_session, barber, weekday=1)
    _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=target_date,
        start_time=time(10, 0),
        status=AppointmentStatus.CANCELADA,
    )

    response = client.get(
        f"/api/v1/availability?service_id={service.id}&date={target_date.isoformat()}"
    )

    assert response.status_code == 200
    starts = [slot["start"] for slot in response.json()["slots"]]
    assert any("T10:00:00" in start for start in starts)


@requires_db
def test_availability_intersects_barber_and_business_hours(client, db_session) -> None:
    service = _create_service(db_session)
    barber = _create_barber(db_session, display_name="Ana")
    _assign_service(db_session, barber, service)
    target_date = _next_weekday(0)
    _set_barber_availability(
        db_session,
        barber,
        weekday=1,
        start_time=time(9, 0),
        end_time=time(17, 0),
    )
    _set_business_hours(
        db_session,
        weekday=1,
        open_time=time(10, 0),
        close_time=time(18, 0),
    )

    response = client.get(
        f"/api/v1/availability?service_id={service.id}&date={target_date.isoformat()}"
    )

    assert response.status_code == 200
    starts = [slot["start"] for slot in response.json()["slots"]]
    assert "T10:00:00" in starts[0]
    assert "T16:30:00" in starts[-1]


@requires_db
def test_availability_returns_no_slots_when_business_closed(client, db_session) -> None:
    service = _create_service(db_session)
    barber = _create_barber(db_session, display_name="Ana")
    _assign_service(db_session, barber, service)
    target_date = _next_weekday(0)
    _set_barber_availability(db_session, barber, weekday=1)
    _set_business_hours(db_session, weekday=1, is_closed=True)

    response = client.get(
        f"/api/v1/availability?service_id={service.id}&date={target_date.isoformat()}"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["barbers"] == []
    assert body["slots"] == []


@requires_db
def test_availability_filters_slots_by_barber_id(client, db_session) -> None:
    service = _create_service(db_session)
    barber_a = _create_barber(db_session, display_name="Ana")
    barber_b = _create_barber(db_session, display_name="Luis")
    _assign_service(db_session, barber_a, service)
    _assign_service(db_session, barber_b, service)
    target_date = _next_weekday(0)
    _set_barber_availability(db_session, barber_a, weekday=1)
    _set_barber_availability(db_session, barber_b, weekday=1)

    response = client.get(
        f"/api/v1/availability?service_id={service.id}&date={target_date.isoformat()}"
        f"&barber_id={barber_a.id}"
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["barbers"]) == 1
    assert all(slot["barber_user_id"] == str(barber_a.id) for slot in body["slots"])


@requires_db
def test_availability_respects_long_service_duration(client, db_session) -> None:
    service = _create_service(db_session, duration_minutes=60)
    barber = _create_barber(db_session, display_name="Ana")
    _assign_service(db_session, barber, service)
    target_date = _next_weekday(0)
    _set_barber_availability(
        db_session,
        barber,
        weekday=1,
        start_time=time(9, 0),
        end_time=time(10, 30),
    )

    response = client.get(
        f"/api/v1/availability?service_id={service.id}&date={target_date.isoformat()}"
    )

    assert response.status_code == 200
    slots = response.json()["slots"]
    assert len(slots) == 3
    assert "T09:00:00" in slots[0]["start"]
    assert "T10:00:00" in slots[0]["end"]
    assert "T09:30:00" in slots[-1]["start"]
    assert "T10:30:00" in slots[-1]["end"]
