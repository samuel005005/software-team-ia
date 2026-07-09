from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.application.appointments.list_barber_schedule import (
    ListBarberScheduleQuery,
    ListMyBarberScheduleUseCase,
)
from app.application.appointments.update_barber_appointment_status import (
    UpdateBarberAppointmentStatusCommand,
    UpdateBarberAppointmentStatusUseCase,
)
from app.application.schedules.barber_availability import (
    BarberAvailabilityBlockCommand,
    ListMyBarberAvailabilityUseCase,
    UpdateMyBarberAvailabilityUseCase,
)
from app.core.dependencies.auth import require_barber
from app.core.dependencies.database import get_db
from app.core.config import get_settings
from app.domain.appointments.errors import (
    AppointmentNotFoundError,
    AppointmentNotUpdatableError,
    InvalidScheduleRangeError,
    InvalidStatusTransitionError,
)
from app.domain.schedules.errors import InvalidBarberAvailabilityError
from app.infrastructure.db.models.user import User
from app.schemas.appointments import (
    BarberScheduleAppointmentResponse,
    BarberScheduleResponse,
    UpdateAppointmentStatusRequest,
)
from app.schemas.schedules import (
    BarberAvailabilityBlockSummary,
    BarberAvailabilityListResponse,
    BarberAvailabilityUpdateRequest,
)

router = APIRouter()


def _to_availability_summary(record) -> BarberAvailabilityBlockSummary:
    return BarberAvailabilityBlockSummary(
        weekday=record.weekday,
        start_time=record.start_time,
        end_time=record.end_time,
        is_active=record.is_active,
    )


@router.get("/availability", response_model=BarberAvailabilityListResponse)
def get_my_availability(
    current_user: User = Depends(require_barber),
    db: Session = Depends(get_db),
) -> BarberAvailabilityListResponse:
    records = ListMyBarberAvailabilityUseCase(db).execute(current_user.id)
    return BarberAvailabilityListResponse(
        items=[_to_availability_summary(record) for record in records]
    )


@router.patch("/availability", response_model=BarberAvailabilityListResponse)
def update_my_availability(
    body: BarberAvailabilityUpdateRequest,
    current_user: User = Depends(require_barber),
    db: Session = Depends(get_db),
) -> BarberAvailabilityListResponse:
    use_case = UpdateMyBarberAvailabilityUseCase(db)
    try:
        records = use_case.execute(
            current_user.id,
            [
                BarberAvailabilityBlockCommand(
                    weekday=item.weekday,
                    start_time=item.start_time,
                    end_time=item.end_time,
                    is_active=item.is_active,
                )
                for item in body.items
            ],
        )
        db.commit()
    except InvalidBarberAvailabilityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception:
        db.rollback()
        raise

    return BarberAvailabilityListResponse(
        items=[_to_availability_summary(record) for record in records]
    )


@router.get("/schedule", response_model=BarberScheduleResponse)
def get_my_schedule(
    date_param: date | None = Query(default=None, alias="date"),
    end_date: date | None = Query(default=None, alias="end_date"),
    current_user: User = Depends(require_barber),
    db: Session = Depends(get_db),
) -> BarberScheduleResponse:
    tz = ZoneInfo(get_settings().business_timezone)
    today = datetime.now(tz).date()
    from_date = date_param or today
    to_date = end_date or from_date

    use_case = ListMyBarberScheduleUseCase(db)
    try:
        resolved_from, resolved_to, records = use_case.execute(
            ListBarberScheduleQuery(
                barber_user_id=current_user.id,
                from_date=from_date,
                to_date=to_date,
            )
        )
    except InvalidScheduleRangeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return BarberScheduleResponse(
        from_date=resolved_from,
        to_date=resolved_to,
        items=[
            BarberScheduleAppointmentResponse(
                id=record.id,
                status=record.status,
                scheduled_start=record.scheduled_start,
                scheduled_end=record.scheduled_end,
                service_id=record.service_id,
                service_name=record.service_name,
                client_user_id=record.client_user_id,
                client_display_name=record.client_display_name,
            )
            for record in records
        ],
    )


@router.patch(
    "/appointments/{appointment_id}/status",
    response_model=BarberScheduleAppointmentResponse,
)
def update_appointment_status(
    appointment_id: UUID,
    body: UpdateAppointmentStatusRequest,
    current_user: User = Depends(require_barber),
    db: Session = Depends(get_db),
) -> BarberScheduleAppointmentResponse:
    use_case = UpdateBarberAppointmentStatusUseCase(db)
    try:
        record = use_case.execute(
            UpdateBarberAppointmentStatusCommand(
                appointment_id=appointment_id,
                barber_user_id=current_user.id,
                new_status=body.status,
                now=datetime.now(timezone.utc),
            )
        )
        db.commit()
    except AppointmentNotFoundError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada",
        )
    except InvalidStatusTransitionError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transición de estado no permitida",
        )
    except AppointmentNotUpdatableError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cita no se puede modificar",
        )
    except Exception:
        db.rollback()
        raise

    return BarberScheduleAppointmentResponse(
        id=record.id,
        status=record.status,
        scheduled_start=record.scheduled_start,
        scheduled_end=record.scheduled_end,
        service_id=record.service_id,
        service_name=record.service_name,
        client_user_id=record.client_user_id,
        client_display_name=record.client_display_name,
    )
