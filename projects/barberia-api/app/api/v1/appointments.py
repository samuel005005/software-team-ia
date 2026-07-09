from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.appointments.cancel import CancelAppointmentCommand, CancelAppointmentUseCase
from app.application.appointments.create import CreateAppointmentCommand, CreateAppointmentUseCase
from app.application.appointments.list_my import ListMyAppointmentsQuery, ListMyAppointmentsUseCase
from app.core.dependencies import get_db
from app.core.dependencies.auth import require_client
from app.domain.appointments.errors import (
    AppointmentNotCancellableError,
    AppointmentNotFoundError,
    BarberNotAvailableError,
    CancellationWindowExpiredError,
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


@router.get("", response_model=AppointmentListResponse)
def list_appointments(
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> AppointmentListResponse:
    use_case = ListMyAppointmentsUseCase(db)
    records = use_case.execute(
        ListMyAppointmentsQuery(
            user_id=current_user.id,
            role=current_user.role,
            now=datetime.now(timezone.utc),
        )
    )
    return AppointmentListResponse(
        items=[
            AppointmentResponse(
                id=record.id,
                status=record.status,
                scheduled_start=record.scheduled_start,
                scheduled_end=record.scheduled_end,
                service_id=record.service_id,
                service_name=record.service_name,
                barber_user_id=record.barber_user_id,
                barber_display_name=record.barber_display_name,
            )
            for record in records
        ]
    )


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: UUID,
    current_user: User = Depends(require_client),
    db: Session = Depends(get_db),
) -> AppointmentResponse:
    use_case = CancelAppointmentUseCase(db)
    try:
        result = use_case.execute(
            CancelAppointmentCommand(
                appointment_id=appointment_id,
                client_user_id=current_user.id,
                now=datetime.now(timezone.utc),
            )
        )
        db.commit()
    except AppointmentNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada",
        ) from exc
    except CancellationWindowExpiredError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo puedes cancelar con al menos 2 horas de anticipación",
        ) from exc
    except AppointmentNotCancellableError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cita no se puede cancelar",
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
