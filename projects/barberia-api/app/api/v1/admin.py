from fastapi import APIRouter, status

from app.schemas.common import MessageResponse

router = APIRouter()


@router.get("/services", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def admin_list_services() -> MessageResponse:
    return MessageResponse(detail="Not implemented — see T-041")


@router.get("/barbers", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def admin_list_barbers() -> MessageResponse:
    return MessageResponse(detail="Not implemented — see T-042")


@router.get("/users", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def admin_list_users() -> MessageResponse:
    return MessageResponse(detail="Not implemented — see T-044")


@router.patch("/business-hours", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def admin_update_business_hours() -> MessageResponse:
    return MessageResponse(detail="Not implemented — see T-045")
