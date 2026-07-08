from app.infrastructure.db.base import Base
import app.infrastructure.db.models  # noqa: F401


def test_all_domain_tables_registered() -> None:
    tables = set(Base.metadata.tables.keys())
    expected = {
        "users",
        "client_profiles",
        "barber_profiles",
        "services",
        "barber_services",
        "business_hours",
        "barber_availability",
        "appointments",
        "appointment_status_history",
        "audit_logs",
        "refresh_tokens",
    }
    assert expected.issubset(tables)
