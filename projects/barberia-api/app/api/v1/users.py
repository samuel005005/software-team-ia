from fastapi import APIRouter, status

from app.schemas.common import MessageResponse
from app.schemas.users import UserProfileUpdate

router = APIRouter()


@router.get("/me", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def get_me() -> MessageResponse:
    return MessageResponse(detail="Not implemented — see T-033")


@router.patch("/me", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def update_me(_: UserProfileUpdate) -> MessageResponse:
    return MessageResponse(detail="Not implemented — see T-033")
