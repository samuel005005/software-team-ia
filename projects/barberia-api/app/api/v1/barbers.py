from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies.database import get_db
from app.infrastructure.repositories.barber_repository import BarberRepository
from app.schemas.barbers import BarberListResponse, BarberSummary

router = APIRouter()


@router.get("", response_model=BarberListResponse)
def list_barbers(
    service_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> BarberListResponse:
    barbers = BarberRepository(db).list_bookable(service_id=service_id)
    return BarberListResponse(
        items=[
            BarberSummary(
                user_id=barber.user_id,
                display_name=barber.display_name,
                bio=barber.bio,
                photo_url=barber.photo_url,
                is_bookable=barber.is_bookable,
            )
            for barber in barbers
        ]
    )
