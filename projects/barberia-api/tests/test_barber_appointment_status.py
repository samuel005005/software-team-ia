import uuid
from datetime import date, datetime, time, timedelta

from sqlalchemy import select

from app.domain.enums import AppointmentStatus, UserRole
from app.infrastructure.db.models.appointment import AppointmentStatusHistory
from tests.conftest import requires_db
from tests.test_barber_schedule import (
    _create_appointment,
    _create_user_and_login,
    _login_barber,
    _seed_barber_with_client,
)
from tests.test_create_appointment import (
    TZ,
    _apply_exclusion_constraint,
    _auth,
    _create_barber,
    _register_and_login,
)

STATUS_URL = "/api/v1/barber/appointments/{appointment_id}/status"


def _patch_status(client, token: str, appointment_id, status: str):
    return client.patch(
        STATUS_URL.format(appointment_id=appointment_id),
        headers=_auth(token),
        json={"status": status},
    )


@requires_db
def test_status_update_requires_auth(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    appointment = _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=date(2030, 7, 9),
        start_time=time(10, 0),
    )

    response = _patch_status(client, "", appointment.id, "en_progreso")
    assert response.status_code == 401


@requires_db
def test_status_update_rejects_client(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    appointment = _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=date(2030, 7, 9),
        start_time=time(10, 0),
    )

    token, _ = _register_and_login(client, db_session)
    response = _patch_status(client, token, appointment.id, "en_progreso")
    assert response.status_code == 403


@requires_db
def test_status_update_rejects_admin(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    appointment = _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=date(2030, 7, 9),
        start_time=time(10, 0),
    )

    token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    response = _patch_status(client, token, appointment.id, "en_progreso")
    assert response.status_code == 403


@requires_db
def test_status_update_not_found(client, db_session) -> None:
    token, _ = _login_barber(client, db_session)
    response = _patch_status(client, token, uuid.uuid4(), "en_progreso")
    assert response.status_code == 404


@requires_db
def test_status_update_wrong_barber(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber_a, client_user = _seed_barber_with_client(db_session)
    barber_b = _create_barber(db_session, display_name="Otro Barbero")
    appointment = _create_appointment(
        db_session,
        client=client_user,
        barber=barber_a,
        service=service,
        target_date=date(2030, 7, 9),
        start_time=time(10, 0),
    )

    token, _ = _login_barber(client, db_session, barber=barber_b)
    response = _patch_status(client, token, appointment.id, "en_progreso")
    assert response.status_code == 404


@requires_db
def test_confirmada_to_en_progreso(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    target_date = date(2030, 7, 9)
    appointment = _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=target_date,
        start_time=time(10, 0),
    )

    token, _ = _login_barber(client, db_session, barber=barber)
    response = _patch_status(client, token, appointment.id, "en_progreso")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "en_progreso"
    assert body["client_display_name"] == "Juan Pérez"
    assert body["service_name"] == "Corte"


@requires_db
def test_en_progreso_to_completada(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    appointment = _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=date(2030, 7, 10),
        start_time=time(11, 0),
        status=AppointmentStatus.EN_PROGRESO,
    )

    token, _ = _login_barber(client, db_session, barber=barber)
    response = _patch_status(client, token, appointment.id, "completada")

    assert response.status_code == 200
    assert response.json()["status"] == "completada"


@requires_db
def test_pendiente_to_confirmada(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    appointment = _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=date(2030, 7, 11),
        start_time=time(9, 0),
        status=AppointmentStatus.PENDIENTE,
    )

    token, _ = _login_barber(client, db_session, barber=barber)
    response = _patch_status(client, token, appointment.id, "confirmada")

    assert response.status_code == 200
    assert response.json()["status"] == "confirmada"


@requires_db
def test_confirmada_to_no_show(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    past_date = datetime.now(TZ).date() - timedelta(days=1)
    appointment = _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=past_date,
        start_time=time(10, 0),
    )

    token, _ = _login_barber(client, db_session, barber=barber)
    response = _patch_status(client, token, appointment.id, "no_show")

    assert response.status_code == 200
    assert response.json()["status"] == "no_show"


@requires_db
def test_no_show_before_start_rejected(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    appointment = _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=date(2030, 12, 25),
        start_time=time(10, 0),
    )

    token, _ = _login_barber(client, db_session, barber=barber)
    response = _patch_status(client, token, appointment.id, "no_show")

    assert response.status_code == 400
    assert "no permitida" in response.json()["detail"].lower()


@requires_db
def test_invalid_transition_completada_to_en_progreso(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    appointment = _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=date(2030, 7, 12),
        start_time=time(14, 0),
        status=AppointmentStatus.COMPLETADA,
    )

    token, _ = _login_barber(client, db_session, barber=barber)
    response = _patch_status(client, token, appointment.id, "en_progreso")

    assert response.status_code == 400


@requires_db
def test_invalid_transition_cancelada(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    appointment = _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=date(2030, 7, 13),
        start_time=time(15, 0),
        status=AppointmentStatus.CANCELADA,
    )

    token, _ = _login_barber(client, db_session, barber=barber)
    response = _patch_status(client, token, appointment.id, "en_progreso")

    assert response.status_code == 400


@requires_db
def test_status_history_recorded(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    appointment = _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=date(2030, 7, 14),
        start_time=time(16, 0),
    )

    token, _ = _login_barber(client, db_session, barber=barber)
    response = _patch_status(client, token, appointment.id, "en_progreso")
    assert response.status_code == 200

    history = db_session.scalars(
        select(AppointmentStatusHistory).where(
            AppointmentStatusHistory.appointment_id == appointment.id
        )
    ).all()

    assert len(history) == 1
    row = history[0]
    assert row.from_status == AppointmentStatus.CONFIRMADA
    assert row.to_status == AppointmentStatus.EN_PROGRESO
    assert row.changed_by_user_id == barber.id
    assert row.changed_at is not None


@requires_db
def test_chained_status_transitions_record_multiple_history_rows(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    appointment = _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=date(2030, 7, 16),
        start_time=time(10, 0),
    )

    token, _ = _login_barber(client, db_session, barber=barber)
    assert _patch_status(client, token, appointment.id, "en_progreso").status_code == 200
    assert _patch_status(client, token, appointment.id, "completada").status_code == 200

    history = db_session.scalars(
        select(AppointmentStatusHistory)
        .where(AppointmentStatusHistory.appointment_id == appointment.id)
        .order_by(AppointmentStatusHistory.changed_at.asc())
    ).all()

    assert len(history) == 2
    assert history[0].from_status == AppointmentStatus.CONFIRMADA
    assert history[0].to_status == AppointmentStatus.EN_PROGRESO
    assert history[1].from_status == AppointmentStatus.EN_PROGRESO
    assert history[1].to_status == AppointmentStatus.COMPLETADA
    assert history[0].changed_by_user_id == barber.id
    assert history[1].changed_by_user_id == barber.id


@requires_db
def test_schedule_reflects_new_status(client, db_session) -> None:
    _apply_exclusion_constraint(db_session.get_bind())
    service, barber, client_user = _seed_barber_with_client(db_session)
    target_date = date(2030, 7, 15)
    appointment = _create_appointment(
        db_session,
        client=client_user,
        barber=barber,
        service=service,
        target_date=target_date,
        start_time=time(10, 30),
    )

    token, _ = _login_barber(client, db_session, barber=barber)
    patch_response = _patch_status(client, token, appointment.id, "en_progreso")
    assert patch_response.status_code == 200

    schedule_response = client.get(
        "/api/v1/barber/schedule",
        params={"date": target_date.isoformat()},
        headers=_auth(token),
    )

    assert schedule_response.status_code == 200
    item = schedule_response.json()["items"][0]
    assert item["status"] == "en_progreso"
