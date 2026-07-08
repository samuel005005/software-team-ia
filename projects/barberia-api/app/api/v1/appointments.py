from fastapi import APIRouter, status

from app.schemas.appointments import (
    AppointmentCreateRequest,
    AppointmentListResponse,
    AppointmentResponse,
)

router = APIRouter()


@router.post("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def create_appointment(_: AppointmentCreateRequest) -> AppointmentResponse:
    return AppointmentResponse(
        id="00000000-0000-0000-0000-000000000000",
        status="confirmada",
    )


@router.get("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def list_appointments() -> AppointmentListResponse:
    return AppointmentListResponse(items=[])


@router.patch("/{appointment_id}/cancel", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def cancel_appointment(appointment_id: str) -> AppointmentResponse:
    return AppointmentResponse(id=appointment_id, status="cancelada")
