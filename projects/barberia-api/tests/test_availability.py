import uuid
from datetime import date, time, timedelta
from decimal import Decimal

from app.domain.enums import UserRole
from app.infrastructure.db.models.barber_profile import BarberProfile
from app.infrastructure.db.models.barber_service import BarberService
from app.infrastructure.db.models.schedule import BarberAvailability, BusinessHours
from app.infrastructure.db.models.service import Service
from app.infrastructure.db.models.user import User
from app.infrastructure.security.password_hasher import hash_password
from tests.conftest import requires_db


def _create_service(db_session, *, name: str = "Corte", is_active: bool = True) -> Service:
    service = Service(
        name=name,
        duration_minutes=30,
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


def _assign_service(db_session, barber: User, service: Service) -> None:
    db_session.add(
        BarberService(barber_user_id=barber.id, service_id=service.id)
    )
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


@requires_db
def test_availability_returns_barbers_for_service_and_date(client, db_session) -> None:
    service = _create_service(db_session)
    available = _create_barber(db_session, display_name="Ana Disponible")
    unavailable = _create_barber(db_session, display_name="Carlos Sin Horario")
    _assign_service(db_session, available, service)
    _assign_service(db_session, unavailable, service)

    target_date = _next_weekday(0)  # Monday
    _set_barber_availability(db_session, available, weekday=1)

    response = client.get(
        f"/api/v1/availability?service_id={service.id}&date={target_date.isoformat()}"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["service_id"] == str(service.id)
    assert body["date"] == target_date.isoformat()
    assert len(body["barbers"]) == 1
    assert body["barbers"][0]["display_name"] == "Ana Disponible"
    assert len(body["slots"]) == 31
    assert body["slots"][0]["barber_user_id"] == str(available.id)


@requires_db
def test_availability_excludes_inactive_barbers(client, db_session) -> None:
    service = _create_service(db_session)
    inactive = _create_barber(db_session, display_name="Inactivo", is_active=False)
    _assign_service(db_session, inactive, service)
    target_date = _next_weekday(0)
    _set_barber_availability(db_session, inactive, weekday=1)

    response = client.get(
        f"/api/v1/availability?service_id={service.id}&date={target_date.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json()["barbers"] == []


@requires_db
def test_availability_excludes_non_bookable_barbers(client, db_session) -> None:
    service = _create_service(db_session)
    barber = _create_barber(db_session, display_name="No Reservable", is_bookable=False)
    _assign_service(db_session, barber, service)
    target_date = _next_weekday(0)
    _set_barber_availability(db_session, barber, weekday=1)

    response = client.get(
        f"/api/v1/availability?service_id={service.id}&date={target_date.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json()["barbers"] == []


@requires_db
def test_availability_excludes_barbers_without_service_assignment(client, db_session) -> None:
    service = _create_service(db_session)
    barber = _create_barber(db_session, display_name="Sin Servicio")
    target_date = _next_weekday(0)
    _set_barber_availability(db_session, barber, weekday=1)

    response = client.get(
        f"/api/v1/availability?service_id={service.id}&date={target_date.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json()["barbers"] == []


@requires_db
def test_availability_returns_empty_when_business_closed(client, db_session) -> None:
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
    assert response.json()["barbers"] == []


@requires_db
def test_availability_filters_by_barber_id(client, db_session) -> None:
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
    barbers = response.json()["barbers"]
    assert len(barbers) == 1
    assert barbers[0]["display_name"] == "Ana"


@requires_db
def test_availability_rejects_inactive_service(client, db_session) -> None:
    service = _create_service(db_session, is_active=False)
    target_date = _next_weekday(0)

    response = client.get(
        f"/api/v1/availability?service_id={service.id}&date={target_date.isoformat()}"
    )

    assert response.status_code == 404


@requires_db
def test_availability_rejects_unknown_service(client) -> None:
    target_date = _next_weekday(0)
    unknown_id = uuid.uuid4()

    response = client.get(
        f"/api/v1/availability?service_id={unknown_id}&date={target_date.isoformat()}"
    )

    assert response.status_code == 404


@requires_db
def test_availability_rejects_past_date(client, db_session) -> None:
    service = _create_service(db_session)
    past_date = date.today() - timedelta(days=1)

    response = client.get(
        f"/api/v1/availability?service_id={service.id}&date={past_date.isoformat()}"
    )

    assert response.status_code == 400


@requires_db
def test_availability_excludes_barbers_without_active_availability_block(client, db_session) -> None:
    service = _create_service(db_session)
    barber = _create_barber(db_session, display_name="Bloque Inactivo")
    _assign_service(db_session, barber, service)
    target_date = _next_weekday(0)
    _set_barber_availability(db_session, barber, weekday=1, is_active=False)

    response = client.get(
        f"/api/v1/availability?service_id={service.id}&date={target_date.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json()["barbers"] == []
