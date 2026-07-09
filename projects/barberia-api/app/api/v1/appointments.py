from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.appointments.create import CreateAppointmentCommand, CreateAppointmentUseCase
from app.core.dependencies import get_db
from app.core.dependencies.auth import require_authenticated, require_client
from app.domain.appointments.errors import (
    BarberNotAvailableError,
    PastAppointmentError,
    ServiceNotAvailableError,
    SlotNotAvailableError,
)
from app.infrastructure.db.models.user import User
from app.schemas.appointments import (
    AppointmentCreateRequest,
    AppointmentListResponse,
    AppointmentResponse,
)

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AppointmentResponse)
def create_appointment(
    body: AppointmentCreateRequest,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> AppointmentResponse:
    use_case = CreateAppointmentUseCase(db)
    try:
        result = use_case.execute(
            CreateAppointmentCommand(
                client_user_id=current_user.id,
                barber_user_id=body.barber_user_id,
                service_id=body.service_id,
                scheduled_start=body.scheduled_start,
            )
        )
        db.commit()
    except PastAppointmentError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede reservar en el pasado",
        ) from exc
    except SlotNotAvailableError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El horario ya no está disponible",
        ) from exc
    except ServiceNotAvailableError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no disponible",
        ) from exc
    except BarberNotAvailableError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Barbero no disponible",
        ) from exc
    except Exception:
        db.rollback()
        raise

    return AppointmentResponse(
        id=result.id,
        status=result.status,
        scheduled_start=result.scheduled_start,
        scheduled_end=result.scheduled_end,
        service_id=result.service_id,
        service_name=result.service_name,
        barber_user_id=result.barber_user_id,
        barber_display_name=result.barber_display_name,
    )


@router.get("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def list_appointments(_: User = Depends(require_authenticated)) -> AppointmentListResponse:
    return AppointmentListResponse(items=[])


@router.patch("/{appointment_id}/cancel", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def cancel_appointment(
    appointment_id: str,
    _: User = Depends(require_client),
) -> AppointmentResponse:
    from datetime import datetime, timezone

    placeholder = datetime(1970, 1, 1, tzinfo=timezone.utc)
    return AppointmentResponse(
        id=appointment_id,
        status="cancelada",
        scheduled_start=placeholder,
        scheduled_end=placeholder,
        service_id="00000000-0000-0000-0000-000000000000",
        service_name="",
        barber_user_id="00000000-0000-0000-0000-000000000000",
        barber_display_name="",
    )
