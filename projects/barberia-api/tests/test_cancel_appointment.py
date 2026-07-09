import uuid
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import select

from app.domain.appointments.cancellation import (
    is_client_cancellable_status,
    meets_cancellation_notice,
)
from app.domain.appointments.scheduling import calculate_scheduled_end
from app.domain.enums import AppointmentStatus, UserRole
from app.infrastructure.db.models.appointment import Appointment, AppointmentStatusHistory
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
from tests.test_list_my_appointments import (
    _create_appointment_for_client,
    _create_user_and_login,
    _seed_context,
)

CANCEL_URL = "/api/v1/appointments/{appointment_id}/cancel"


def test_meets_cancellation_notice_allows_exactly_two_hours() -> None:
    now = datetime(2026, 7, 15, 8, 0, tzinfo=TZ)
    scheduled_start = now + timedelta(hours=2)
    assert meets_cancellation_notice(scheduled_start, now, 2) is True


def test_meets_cancellation_notice_rejects_under_two_hours() -> None:
    now = datetime(2026, 7, 15, 8, 0, tzinfo=TZ)
    scheduled_start = now + timedelta(hours=1, minutes=59)
    assert meets_cancellation_notice(scheduled_start, now, 2) is False


def test_is_client_cancellable_status() -> None:
    assert is_client_cancellable_status(AppointmentStatus.CONFIRMADA) is True
    assert is_client_cancellable_status(AppointmentStatus.PENDIENTE) is True
    assert is_client_cancellable_status(AppointmentStatus.CANCELADA) is False
    assert is_client_cancellable_status(AppointmentStatus.COMPLETADA) is False


def _cancel(client, token: str, appointment_id: str) -> object:
    return client.patch(
        CANCEL_URL.format(appointment_id=appointment_id),
        headers=_auth(token),
    )


def _create_appointment_at(
    db_session,
    *,
    client,
    barber,
    service,
    scheduled_start: datetime,
    status: AppointmentStatus = AppointmentStatus.CONFIRMADA,
) -> Appointment:
    appointment = Appointment(
        client_user_id=client.id,
        barber_user_id=barber.id,
        service_id=service.id,
        scheduled_start=scheduled_start,
        scheduled_end=calculate_scheduled_end(scheduled_start, service.duration_minutes),
        status=status,
    )
    db_session.add(appointment)
    db_session.commit()
    return appointment


def _seed_cancel_context(db_session) -> tuple:
    service, barber = _seed_context(db_session)
    token, client = _register_and_login(client=None, db_session=db_session)
    return service, barber, client, token


@requires_db
def test_cancel_requires_auth(client) -> None:
    response = client.patch(
        CANCEL_URL.format(appointment_id=str(uuid.uuid4())),
    )
    assert response.status_code == 401


@requires_db
def test_cancel_requires_client(client, db_session) -> None:
    service, barber = _seed_context(db_session)
    owner = _create_client(db_session)
    target_date = _next_weekday(0)
    appointment = _create_appointment_for_client(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        target_date=target_date,
        start_time=time(10, 0),
    )

    for role in (UserRole.BARBER, UserRole.ADMIN):
        token, _ = _create_user_and_login(client, db_session, role=role)
        response = _cancel(client, token, str(appointment.id))
        assert response.status_code == 403


@requires_db
def test_cancel_success_confirmada(client, db_session) -> None:
    service, barber = _seed_context(db_session)
    token, owner = _register_and_login(client, db_session)
    scheduled_start = datetime.now(TZ) + timedelta(hours=5)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=scheduled_start,
        status=AppointmentStatus.CONFIRMADA,
    )

    response = _cancel(client, token, str(appointment.id))

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "cancelada"
    assert body["service_name"] == "Corte"
    assert body["barber_display_name"] == "Carlos"

    db_session.refresh(appointment)
    assert appointment.status == AppointmentStatus.CANCELADA
    assert appointment.cancelled_at is not None


@requires_db
@pytest.mark.parametrize(
    "initial_status",
    [AppointmentStatus.CONFIRMADA, AppointmentStatus.PENDIENTE],
)
def test_cancel_records_status_history(client, db_session, initial_status) -> None:
    service, barber = _seed_context(db_session)
    token, owner = _register_and_login(client, db_session)
    scheduled_start = datetime.now(TZ) + timedelta(hours=5)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=scheduled_start,
        status=initial_status,
    )

    response = _cancel(client, token, str(appointment.id))
    assert response.status_code == 200

    history = db_session.scalars(
        select(AppointmentStatusHistory).where(
            AppointmentStatusHistory.appointment_id == appointment.id
        )
    ).all()

    assert len(history) == 1
    row = history[0]
    assert row.from_status == initial_status
    assert row.to_status == AppointmentStatus.CANCELADA
    assert row.changed_by_user_id == owner.id
    assert row.changed_at is not None


@requires_db
def test_cancel_success_pendiente(client, db_session) -> None:
    service, barber = _seed_context(db_session)
    token, owner = _register_and_login(client, db_session)
    scheduled_start = datetime.now(TZ) + timedelta(hours=5)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=scheduled_start,
        status=AppointmentStatus.PENDIENTE,
    )

    response = _cancel(client, token, str(appointment.id))

    assert response.status_code == 200
    assert response.json()["status"] == "cancelada"


@requires_db
def test_cancel_rejects_other_client_appointment(client, db_session) -> None:
    service, barber = _seed_context(db_session)
    owner = _create_client(db_session)
    token, _ = _register_and_login(client, db_session)
    scheduled_start = datetime.now(TZ) + timedelta(hours=5)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=scheduled_start,
    )

    response = _cancel(client, token, str(appointment.id))

    assert response.status_code == 404
    assert "no encontrada" in response.json()["detail"].lower()


@requires_db
def test_cancel_rejects_unknown_id(client, db_session) -> None:
    token, _ = _register_and_login(client, db_session)

    response = _cancel(client, token, str(uuid.uuid4()))

    assert response.status_code == 404


@requires_db
def test_cancel_rejects_within_two_hours(client, db_session) -> None:
    service, barber = _seed_context(db_session)
    token, owner = _register_and_login(client, db_session)
    scheduled_start = datetime.now(TZ) + timedelta(hours=1)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=scheduled_start,
    )

    response = _cancel(client, token, str(appointment.id))

    assert response.status_code == 400
    assert "2 horas" in response.json()["detail"]


@requires_db
def test_cancel_allows_at_least_two_hours(client, db_session) -> None:
    service, barber = _seed_context(db_session)
    token, owner = _register_and_login(client, db_session)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=datetime.now(TZ) + timedelta(hours=2, minutes=1),
    )

    response = _cancel(client, token, str(appointment.id))

    assert response.status_code == 200
    assert response.json()["status"] == "cancelada"


@requires_db
def test_cancel_rejects_already_cancelled(client, db_session) -> None:
    service, barber = _seed_context(db_session)
    token, owner = _register_and_login(client, db_session)
    scheduled_start = datetime.now(TZ) + timedelta(hours=5)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=scheduled_start,
        status=AppointmentStatus.CANCELADA,
    )

    response = _cancel(client, token, str(appointment.id))

    assert response.status_code == 400
    assert "no se puede cancelar" in response.json()["detail"].lower()


@requires_db
def test_cancel_rejects_completed(client, db_session) -> None:
    service, barber = _seed_context(db_session)
    token, owner = _register_and_login(client, db_session)
    scheduled_start = datetime.now(TZ) + timedelta(hours=5)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=scheduled_start,
        status=AppointmentStatus.COMPLETADA,
    )

    response = _cancel(client, token, str(appointment.id))

    assert response.status_code == 400


@requires_db
def test_cancel_rejects_en_progreso(client, db_session) -> None:
    service, barber = _seed_context(db_session)
    token, owner = _register_and_login(client, db_session)
    scheduled_start = datetime.now(TZ) + timedelta(hours=5)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=scheduled_start,
        status=AppointmentStatus.EN_PROGRESO,
    )

    response = _cancel(client, token, str(appointment.id))

    assert response.status_code == 400


@requires_db
def test_cancel_rejects_past_appointment(client, db_session) -> None:
    service, barber = _seed_context(db_session)
    token, owner = _register_and_login(client, db_session)
    scheduled_start = datetime.now(TZ) - timedelta(hours=1)
    appointment = _create_appointment_at(
        db_session,
        client=owner,
        barber=barber,
        service=service,
        scheduled_start=scheduled_start,
    )

    response = _cancel(client, token, str(appointment.id))

    assert response.status_code == 400
    assert "no se puede cancelar" in response.json()["detail"].lower()


@requires_db
def test_cancel_frees_slot_for_availability(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber = _seed_context(db_session)
    token, owner = _register_and_login(client, db_session)
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

    cancel_response = _cancel(client, token, str(appointment.id))
    assert cancel_response.status_code == 200

    after = client.get(
        f"/api/v1/availability?service_id={service.id}&date={target_date.isoformat()}"
    )
    assert after.status_code == 200
    after_starts = [slot["start"] for slot in after.json()["slots"]]
    assert any("T10:00:00" in start for start in after_starts)
