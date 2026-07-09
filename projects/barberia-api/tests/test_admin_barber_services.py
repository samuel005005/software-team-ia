import uuid
from decimal import Decimal

from app.domain.enums import UserRole
from app.infrastructure.db.models.barber_profile import BarberProfile
from app.infrastructure.db.models.barber_service import BarberService
from app.infrastructure.db.models.service import Service
from app.infrastructure.db.models.user import User
from app.infrastructure.security.password_hasher import hash_password
from tests.conftest import requires_db
from tests.test_role_guards import _auth, _create_user_and_login


def _create_service(db_session, *, name: str, is_active: bool = True) -> Service:
    service = Service(
        name=name,
        duration_minutes=30,
        price_dop=Decimal("350.00"),
        is_active=is_active,
    )
    db_session.add(service)
    db_session.commit()
    return service


def _create_barber(db_session, *, display_name: str = "Barbero Test") -> User:
    user = User(
        email=f"barber-{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.BARBER,
        is_active=True,
    )
    user.barber_profile = BarberProfile(display_name=display_name, is_bookable=True)
    db_session.add(user)
    db_session.commit()
    return user


@requires_db
def test_admin_get_barber_services_empty(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    barber = _create_barber(db_session)

    response = client.get(
        f"/api/v1/admin/barbers/{barber.id}/services",
        headers=_auth(admin_token),
    )

    assert response.status_code == 200
    assert response.json()["items"] == []


@requires_db
def test_admin_set_barber_services(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    barber = _create_barber(db_session)
    service_a = _create_service(db_session, name="Corte")
    service_b = _create_service(db_session, name="Afeitado")

    response = client.put(
        f"/api/v1/admin/barbers/{barber.id}/services",
        headers=_auth(admin_token),
        json={"service_ids": [str(service_a.id), str(service_b.id)]},
    )

    assert response.status_code == 200
    names = [item["name"] for item in response.json()["items"]]
    assert names == ["Afeitado", "Corte"]

    filtered = client.get(f"/api/v1/barbers?service_id={service_a.id}")
    assert len(filtered.json()["items"]) == 1
    assert filtered.json()["items"][0]["display_name"] == "Barbero Test"

    other = client.get(f"/api/v1/barbers?service_id={service_b.id}")
    assert len(other.json()["items"]) == 1


@requires_db
def test_admin_set_barber_services_rejects_inactive(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    barber = _create_barber(db_session)
    inactive = _create_service(db_session, name="Inactivo", is_active=False)

    response = client.put(
        f"/api/v1/admin/barbers/{barber.id}/services",
        headers=_auth(admin_token),
        json={"service_ids": [str(inactive.id)]},
    )

    assert response.status_code == 400


@requires_db
def test_admin_set_barber_services_replaces_existing(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    barber = _create_barber(db_session)
    service_a = _create_service(db_session, name="Corte")
    service_b = _create_service(db_session, name="Afeitado")

    client.put(
        f"/api/v1/admin/barbers/{barber.id}/services",
        headers=_auth(admin_token),
        json={"service_ids": [str(service_a.id)]},
    )
    response = client.put(
        f"/api/v1/admin/barbers/{barber.id}/services",
        headers=_auth(admin_token),
        json={"service_ids": [str(service_b.id)]},
    )

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["name"] == "Afeitado"

    filtered = client.get(f"/api/v1/barbers?service_id={service_a.id}")
    assert filtered.json()["items"] == []
