from fastapi import APIRouter, status

from app.schemas.barbers import BarberListResponse

router = APIRouter()


@router.get("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def list_barbers() -> BarberListResponse:
    return BarberListResponse(items=[])
