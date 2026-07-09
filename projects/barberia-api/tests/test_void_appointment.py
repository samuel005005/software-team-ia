import uuid
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import select

from app.domain.appointments.cancellation import is_admin_voidable_status
from app.domain.appointments.scheduling import calculate_scheduled_end
from app.domain.enums import AppointmentStatus, UserRole
from app.infrastructure.db.models.appointment import (
    Appointment,
    AppointmentStatusHistory,
    AuditLog,
)
from tests.conftest import requires_db
from tests.test_cancel_appointment import (
    TZ,
    _apply_exclusion_constraint,
    _create_appointment_at,
    _seed_context,
)
from tests.test_create_appointment import (
    _auth,
    _create_client,
    _next_weekday,
    _register_and_login,
)
from tests.test_barber_schedule import _login_barber
from tests.test_list_my_appointments import (
    _create_appointment_for_client,
    _create_user_and_login,
)
from tests.test_role_guards import _auth as role_guard_auth

VOID_URL = "/api/v1/admin/appointments/{appointment_id}/void"


def test_is_admin_voidable_status() -> None:
    assert is_admin_voidable_status(AppointmentStatus.PENDIENTE) is True
    assert is_admin_voidable_status(AppointmentStatus.CONFIRMADA) is True
    assert is_admin_voidable_status(AppointmentStatus.EN_PROGRESO) is True
    assert is_admin_voidable_status(AppointmentStatus.NO_SHOW) is True
    assert is_admin_voidable_status(AppointmentStatus.COMPLETADA) is False
    assert is_admin_voidable_status(AppointmentStatus.CANCELADA) is False


def _void(client, token: str, appointment_id: str, *, reason: str = "Emergencia operativa") -> object:
    return client.patch(
        VOID_URL.format(appointment_id=appointment_id),
        headers=_auth(token),
        json={"reason": reason},
    )


@requires_db
def test_void_requires_auth(client) -> None:
    response = client.patch(
        VOID_URL.format(appointment_id=str(uuid.uuid4())),
        json={"reason": "Emergencia operativa"},
    )
    assert response.status_code == 401


@requires_db
def test_void_requires_admin(client, db_session) -> None:
    service, barber = _seed_context(db_session)
    owner = _create_client(db_session)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=datetime.now(TZ) + timedelta(hours=5),
    )

    for role in (UserRole.CLIENT, UserRole.BARBER):
        token, _ = _create_user_and_login(client, db_session, role=role)
        response = _void(client, token, str(appointment.id))
        assert response.status_code == 403


@requires_db
def test_void_success_confirmada(client, db_session) -> None:
    service, barber = _seed_context(db_session)
    owner = _create_client(db_session)
    admin_token, admin = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=datetime.now(TZ) + timedelta(hours=5),
        status=AppointmentStatus.CONFIRMADA,
    )

    response = _void(client, admin_token, str(appointment.id), reason="Conflicto de agenda")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "cancelada"
    assert body["service_name"] == "Corte"

    db_session.refresh(appointment)
    assert appointment.status == AppointmentStatus.CANCELADA
    assert appointment.cancelled_at is not None
    assert appointment.cancellation_reason == "Conflicto de agenda"


@requires_db
@pytest.mark.parametrize(
    "initial_status",
    [
        AppointmentStatus.PENDIENTE,
        AppointmentStatus.CONFIRMADA,
        AppointmentStatus.EN_PROGRESO,
        AppointmentStatus.NO_SHOW,
    ],
)
def test_void_allows_voidable_statuses(client, db_session, initial_status) -> None:
    service, barber = _seed_context(db_session)
    owner = _create_client(db_session)
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=datetime.now(TZ) + timedelta(hours=5),
        status=initial_status,
    )

    response = _void(client, admin_token, str(appointment.id))

    assert response.status_code == 200
    assert response.json()["status"] == "cancelada"


@requires_db
@pytest.mark.parametrize(
    "initial_status",
    [AppointmentStatus.COMPLETADA, AppointmentStatus.CANCELADA],
)
def test_void_rejects_terminal_statuses(client, db_session, initial_status) -> None:
    service, barber = _seed_context(db_session)
    owner = _create_client(db_session)
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=datetime.now(TZ) + timedelta(hours=5),
        status=initial_status,
    )

    response = _void(client, admin_token, str(appointment.id))

    assert response.status_code == 400
    assert "no se puede anular" in response.json()["detail"].lower()


@requires_db
def test_void_rejects_unknown_id(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)

    response = _void(client, admin_token, str(uuid.uuid4()))

    assert response.status_code == 404


@requires_db
@pytest.mark.parametrize(
    "payload",
    [{}, {"reason": ""}, {"reason": "ab"}],
)
def test_void_rejects_invalid_reason(client, db_session, payload) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)

    response = client.patch(
        VOID_URL.format(appointment_id=str(uuid.uuid4())),
        headers=role_guard_auth(admin_token),
        json=payload,
    )

    assert response.status_code == 422


@requires_db
def test_void_records_status_history(client, db_session) -> None:
    service, barber = _seed_context(db_session)
    owner = _create_client(db_session)
    admin_token, admin = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=datetime.now(TZ) + timedelta(hours=5),
        status=AppointmentStatus.CONFIRMADA,
    )

    response = _void(client, admin_token, str(appointment.id))
    assert response.status_code == 200

    history = db_session.scalars(
        select(AppointmentStatusHistory).where(
            AppointmentStatusHistory.appointment_id == appointment.id
        )
    ).all()

    assert len(history) == 1
    row = history[0]
    assert row.from_status == AppointmentStatus.CONFIRMADA
    assert row.to_status == AppointmentStatus.CANCELADA
    assert row.changed_by_user_id == admin.id


@requires_db
def test_void_records_audit_log(client, db_session) -> None:
    service, barber = _seed_context(db_session)
    owner = _create_client(db_session)
    admin_token, admin = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=datetime.now(TZ) + timedelta(hours=5),
        status=AppointmentStatus.EN_PROGRESO,
    )

    response = _void(client, admin_token, str(appointment.id), reason="Emergencia médica")
    assert response.status_code == 200

    logs = db_session.scalars(
        select(AuditLog).where(AuditLog.entity_id == appointment.id)
    ).all()

    assert len(logs) == 1
    log = logs[0]
    assert log.action == "appointment_voided"
    assert log.entity_type == "appointment"
    assert log.actor_user_id == admin.id
    assert log.metadata_json["reason"] == "Emergencia médica"
    assert log.metadata_json["from_status"] == "en_progreso"


@requires_db
def test_void_frees_slot_for_availability(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber = _seed_context(db_session)
    owner = _create_client(db_session)
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    target_date = _next_weekday(0)
    start_time = time(10, 0)
    appointment = _create_appointment_for_client(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        target_date=target_date,
        start_time=start_time,
    )

    before = client.get(
        f"/api/v1/availability?service_id={service.id}&date={target_date.isoformat()}"
    )
    assert before.status_code == 200
    before_starts = [slot["start"] for slot in before.json()["slots"]]
    assert not any("T10:00:00" in start for start in before_starts)

    void_response = _void(client, admin_token, str(appointment.id))
    assert void_response.status_code == 200

    after = client.get(
        f"/api/v1/availability?service_id={service.id}&date={target_date.isoformat()}"
    )
    assert after.status_code == 200
    after_starts = [slot["start"] for slot in after.json()["slots"]]
    assert any("T10:00:00" in start for start in after_starts)


@requires_db
def test_void_visible_to_client(client, db_session) -> None:
    service, barber = _seed_context(db_session)
    client_token, owner = _register_and_login(client, db_session)
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=datetime.now(TZ) + timedelta(hours=5),
    )

    void_response = _void(client, admin_token, str(appointment.id))
    assert void_response.status_code == 200

    list_response = client.get("/api/v1/appointments", headers=_auth(client_token))
    assert list_response.status_code == 200
    items = list_response.json()["items"]
    assert len(items) == 1
    assert items[0]["status"] == "cancelada"


@requires_db
def test_void_visible_to_barber(client, db_session) -> None:
    service, barber = _seed_context(db_session)
    owner = _create_client(db_session)
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    scheduled_start = datetime.now(TZ) + timedelta(days=1)
    appointment = Appointment(
        client_user_id=owner.id,
        barber_user_id=barber.id,
        service_id=service.id,
        scheduled_start=scheduled_start,
        scheduled_end=calculate_scheduled_end(scheduled_start, service.duration_minutes),
        status=AppointmentStatus.CONFIRMADA,
    )
    db_session.add(appointment)
    db_session.commit()

    barber_token, _ = _login_barber(client, db_session, barber=barber)
    void_response = _void(client, admin_token, str(appointment.id))
    assert void_response.status_code == 200

    target_date = scheduled_start.date().isoformat()
    schedule_response = client.get(
        "/api/v1/barber/schedule",
        params={"date": target_date},
        headers=_auth(barber_token),
    )
    assert schedule_response.status_code == 200
    items = schedule_response.json()["items"]
    assert len(items) == 1
    assert items[0]["status"] == "cancelada"
