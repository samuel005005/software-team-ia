from fastapi import APIRouter, Query, status

from app.schemas.availability import AvailabilityResponse

router = APIRouter()


@router.get("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def get_availability(
    service_id: str = Query(...),
    date: str = Query(..., description="YYYY-MM-DD"),
    barber_id: str | None = Query(default=None),
) -> AvailabilityResponse:
    return AvailabilityResponse(service_id=service_id, date=date, slots=[])
