from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.application.availability.get_availability import GetAvailabilityUseCase
from app.core.dependencies.database import get_db
from app.domain.availability.errors import InvalidDateError, ServiceNotAvailableError
from app.schemas.availability import AvailabilityResponse
from app.schemas.barbers import BarberSummary

router = APIRouter()


@router.get("", response_model=AvailabilityResponse)
def get_availability(
    service_id: UUID = Query(...),
    date: date = Query(..., description="YYYY-MM-DD"),
    barber_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> AvailabilityResponse:
    use_case = GetAvailabilityUseCase(db)
    try:
        result = use_case.execute(service_id, date, barber_id)
    except ServiceNotAvailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no disponible",
        ) from exc
    except InvalidDateError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return AvailabilityResponse(
        service_id=service_id,
        date=date,
        barbers=[
            BarberSummary(
                user_id=barber.user_id,
                display_name=barber.display_name,
                bio=barber.bio,
                photo_url=barber.photo_url,
                is_bookable=barber.is_bookable,
            )
            for barber in result.barbers
        ],
        slots=result.slots,
    )
