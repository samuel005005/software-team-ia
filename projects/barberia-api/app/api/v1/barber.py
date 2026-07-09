from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.schedules.barber_availability import (
    BarberAvailabilityBlockCommand,
    ListMyBarberAvailabilityUseCase,
    UpdateMyBarberAvailabilityUseCase,
)
from app.core.dependencies.auth import require_barber
from app.core.dependencies.database import get_db
from app.domain.schedules.errors import InvalidBarberAvailabilityError
from app.infrastructure.db.models.user import User
from app.schemas.common import MessageResponse
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


@router.patch(
    "/appointments/{appointment_id}/status",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
def update_appointment_status(
    appointment_id: str,
    _: User = Depends(require_barber),
) -> MessageResponse:
    return MessageResponse(detail=f"Not implemented — see T-053 ({appointment_id})")
