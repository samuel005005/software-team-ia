import os
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.appointments.scheduling import calculate_scheduled_end
from app.domain.enums import AppointmentStatus, UserRole
from app.infrastructure.db.base import Base
import app.infrastructure.db.models  # noqa: F401
from app.infrastructure.db.models.appointment import Appointment
from app.infrastructure.db.models.barber_profile import BarberProfile
from app.infrastructure.db.models.client_profile import ClientProfile
from app.infrastructure.db.models.service import Service
from app.infrastructure.db.models.user import User

DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://barberia:barberia@localhost:5433/barberia_test",
)


def _db_available() -> bool:
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_available(), reason="PostgreSQL test DB not available")


@pytest.fixture
def db_session() -> Session:
    engine = create_engine(DATABASE_URL)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    _apply_exclusion_constraint(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


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


def _seed_appointment_context(session: Session) -> tuple[User, User, Service]:
    client = User(email="client@test.com", password_hash="hash", role=UserRole.CLIENT)
    barber_user = User(email="barber@test.com", password_hash="hash", role=UserRole.BARBER)
    session.add_all([client, barber_user])
    session.flush()

    session.add(ClientProfile(user_id=client.id, full_name="Cliente", phone="8090000000"))
    session.add(BarberProfile(user_id=barber_user.id, display_name="Barbero"))
    service = Service(name="Corte", duration_minutes=30, price_dop="500.00")
    session.add(service)
    session.flush()
    return client, barber_user, service


def test_calculate_scheduled_end() -> None:
    start = datetime(2026, 7, 8, 10, 0, tzinfo=timezone.utc)
    end = calculate_scheduled_end(start, 30)
    assert end == start + timedelta(minutes=30)


def test_calculate_scheduled_end_rejects_invalid_duration() -> None:
    with pytest.raises(ValueError):
        calculate_scheduled_end(datetime.now(timezone.utc), 0)


def test_appointment_overlap_rejected(db_session: Session) -> None:
    client, barber, service = _seed_appointment_context(db_session)
    start = datetime(2026, 7, 10, 10, 0, tzinfo=timezone.utc)

    first = Appointment(
        client_user_id=client.id,
        barber_user_id=barber.id,
        service_id=service.id,
        scheduled_start=start,
        scheduled_end=calculate_scheduled_end(start, 30),
        status=AppointmentStatus.CONFIRMADA,
    )
    db_session.add(first)
    db_session.commit()

    overlap_start = start + timedelta(minutes=15)
    second = Appointment(
        client_user_id=client.id,
        barber_user_id=barber.id,
        service_id=service.id,
        scheduled_start=overlap_start,
        scheduled_end=calculate_scheduled_end(overlap_start, 30),
        status=AppointmentStatus.CONFIRMADA,
    )
    db_session.add(second)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_cancelled_appointment_does_not_block_slot(db_session: Session) -> None:
    client, barber, service = _seed_appointment_context(db_session)
    start = datetime(2026, 7, 11, 10, 0, tzinfo=timezone.utc)

    cancelled = Appointment(
        client_user_id=client.id,
        barber_user_id=barber.id,
        service_id=service.id,
        scheduled_start=start,
        scheduled_end=calculate_scheduled_end(start, 30),
        status=AppointmentStatus.CANCELADA,
    )
    db_session.add(cancelled)
    db_session.commit()

    replacement = Appointment(
        client_user_id=client.id,
        barber_user_id=barber.id,
        service_id=service.id,
        scheduled_start=start,
        scheduled_end=calculate_scheduled_end(start, 30),
        status=AppointmentStatus.CONFIRMADA,
    )
    db_session.add(replacement)
    db_session.commit()
