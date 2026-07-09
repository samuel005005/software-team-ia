import uuid
from datetime import datetime, timedelta, timezone

from app.domain.enums import AppointmentStatus, UserRole
from app.infrastructure.db.models.appointment import Appointment
from app.infrastructure.db.models.barber_profile import BarberProfile
from app.infrastructure.db.models.client_profile import ClientProfile
from app.infrastructure.db.models.service import Service
from app.infrastructure.db.models.user import User
from app.infrastructure.security.password_hasher import hash_password
from tests.conftest import requires_db
from tests.test_role_guards import _auth, _create_user_and_login, _register_client


def _create_client(
    db_session,
    *,
    email: str | None = None,
    full_name: str = "Cliente Test",
    phone: str = "8095551111",
    is_active: bool = True,
) -> User:
    user = User(
        email=email or f"client-{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.CLIENT,
        is_active=is_active,
    )
    user.client_profile = ClientProfile(
        full_name=full_name,
        phone=phone,
    )
    db_session.add(user)
    db_session.commit()
    return user


def _create_appointment(
    db_session,
    *,
    client: User,
    barber: User,
    service: Service,
    status: AppointmentStatus = AppointmentStatus.CONFIRMADA,
) -> Appointment:
    start = datetime.now(timezone.utc) + timedelta(days=1)
    appointment = Appointment(
        client_user_id=client.id,
        barber_user_id=barber.id,
        service_id=service.id,
        scheduled_start=start,
        scheduled_end=start + timedelta(minutes=service.duration_minutes),
        status=status,
    )
    db_session.add(appointment)
    db_session.commit()
    return appointment


@requires_db
def test_admin_list_clients_includes_inactive(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    _create_client(db_session, full_name="Activo")
    _create_client(db_session, full_name="Inactivo", is_active=False)

    response = client.get("/api/v1/admin/users", headers=_auth(admin_token))

    assert response.status_code == 200
    names = {item["full_name"] for item in response.json()["items"]}
    assert names == {"Activo", "Inactivo"}


@requires_db
def test_admin_update_client_deactivates(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    client_user = _create_client(db_session, full_name="Temporal")

    response = client.patch(
        f"/api/v1/admin/users/{client_user.id}",
        headers=_auth(admin_token),
        json={"is_active": False},
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


@requires_db
def test_admin_list_client_appointments(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    client_user = _create_client(db_session, full_name="Con citas")
    barber = User(
        email=f"barber-{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.BARBER,
        is_active=True,
    )
    barber.barber_profile = BarberProfile(display_name="Barbero Uno")
    service = Service(name="Corte", duration_minutes=30, price_dop="500.00")
    db_session.add_all([barber, service])
    db_session.commit()

    _create_appointment(db_session, client=client_user, barber=barber, service=service)

    response = client.get(
        f"/api/v1/admin/users/{client_user.id}/appointments",
        headers=_auth(admin_token),
    )

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["service_name"] == "Corte"
    assert items[0]["barber_display_name"] == "Barbero Uno"
    assert items[0]["status"] == "confirmada"


@requires_db
def test_admin_clients_forbidden_for_client(client, db_session) -> None:
    client_token, _ = _register_client(client)

    response = client.get("/api/v1/admin/users", headers=_auth(client_token))

    assert response.status_code == 403


@requires_db
def test_admin_client_not_found(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)

    response = client.get(
        f"/api/v1/admin/users/{uuid.uuid4()}/appointments",
        headers=_auth(admin_token),
    )

    assert response.status_code == 404
