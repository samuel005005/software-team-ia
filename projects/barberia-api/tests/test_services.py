from decimal import Decimal

from app.infrastructure.db.models.service import Service
from tests.conftest import requires_db


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
def test_list_services_returns_active_only_sorted_by_name(client, db_session) -> None:
    _create_service(db_session, name="Corte clásico", duration_minutes=30, price_dop="400.00")
    _create_service(
        db_session,
        name="Afeitado",
        duration_minutes=20,
        price_dop="250.50",
        description="Afeitado tradicional",
    )
    _create_service(db_session, name="Servicio oculto", is_active=False)

    response = client.get("/api/v1/services")

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 2
    assert body["items"][0]["name"] == "Afeitado"
    assert body["items"][0]["duration_minutes"] == 20
    assert body["items"][0]["price_dop"] == "250.50"
    assert body["items"][0]["description"] == "Afeitado tradicional"
    assert body["items"][1]["name"] == "Corte clásico"
    assert body["items"][1]["price_dop"] == "400.00"


@requires_db
def test_list_services_empty_when_none_active(client) -> None:
    response = client.get("/api/v1/services")

    assert response.status_code == 200
    assert response.json()["items"] == []
