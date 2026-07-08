from fastapi import APIRouter, status

from app.schemas.services import ServiceListResponse

router = APIRouter()


@router.get("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def list_services() -> ServiceListResponse:
    return ServiceListResponse(items=[])
