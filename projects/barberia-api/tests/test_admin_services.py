import uuid
from decimal import Decimal

from app.domain.enums import UserRole
from app.infrastructure.db.models.service import Service
from app.infrastructure.security.password_hasher import hash_password
from app.infrastructure.db.models.user import User
from tests.conftest import requires_db
from tests.test_role_guards import _auth, _create_user_and_login, _register_client


def _create_service(
    db_session,
    *,
    name: str,
    duration_minutes: int = 30,
    price_dop: str = "350.00",
    description: str | None = None,
    is_active: bool = True,
) -> Service:
    service = Service(
        name=name,
        description=description,
        duration_minutes=duration_minutes,
        price_dop=Decimal(price_dop),
        is_active=is_active,
    )
    db_session.add(service)
    db_session.commit()
    return service


@requires_db
def test_admin_list_services_includes_inactive(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    _create_service(db_session, name="Activo")
    _create_service(db_session, name="Inactivo", is_active=False)

    response = client.get("/api/v1/admin/services", headers=_auth(admin_token))

    assert response.status_code == 200
    names = [item["name"] for item in response.json()["items"]]
    assert names == ["Activo", "Inactivo"]


@requires_db
def test_admin_create_service(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)

    response = client.post(
        "/api/v1/admin/services",
        headers=_auth(admin_token),
        json={
            "name": "Corte premium",
            "description": "Incluye styling",
            "duration_minutes": 45,
            "price_dop": "550.00",
            "is_active": True,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Corte premium"
    assert body["duration_minutes"] == 45
    assert body["price_dop"] == "550.00"

    public = client.get("/api/v1/services")
    assert len(public.json()["items"]) == 1


@requires_db
def test_admin_update_service_deactivates(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    service = _create_service(db_session, name="Temporal")

    response = client.patch(
        f"/api/v1/admin/services/{service.id}",
        headers=_auth(admin_token),
        json={"is_active": False, "price_dop": "375.00"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["is_active"] is False
    assert body["price_dop"] == "375.00"

    public = client.get("/api/v1/services")
    assert public.json()["items"] == []


@requires_db
def test_admin_services_reject_client(client) -> None:
    token, _ = _register_client(client)
    response = client.get("/api/v1/admin/services", headers=_auth(token))
    assert response.status_code == 403


@requires_db
def test_admin_update_missing_service_returns_404(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    missing_id = uuid.uuid4()

    response = client.patch(
        f"/api/v1/admin/services/{missing_id}",
        headers=_auth(admin_token),
        json={"name": "No existe"},
    )

    assert response.status_code == 404
