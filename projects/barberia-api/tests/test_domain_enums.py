from app.domain.enums import AppointmentStatus, UserRole, Weekday


def test_user_role_values() -> None:
    assert UserRole.CLIENT == "client"
    assert UserRole.BARBER == "barber"
    assert UserRole.ADMIN == "admin"


def test_appointment_status_includes_spec_states() -> None:
    values = {status.value for status in AppointmentStatus}
    assert "pendiente" in values
    assert "confirmada" in values
    assert "cancelada" in values


def test_weekday_range() -> None:
    assert Weekday.MONDAY == 1
    assert Weekday.SUNDAY == 7
