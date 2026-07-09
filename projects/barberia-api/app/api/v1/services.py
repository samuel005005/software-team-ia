from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.services.list_active import ListActiveServicesUseCase
from app.core.dependencies.database import get_db
from app.schemas.services import ServiceListResponse, ServiceSummary

router = APIRouter()


def _to_summary(service) -> ServiceSummary:
    return ServiceSummary(
        id=service.id,
        name=service.name,
        description=service.description,
        duration_minutes=service.duration_minutes,
        price_dop=service.price_dop,
        is_active=service.is_active,
    )


@router.get("", response_model=ServiceListResponse)
def list_services(db: Session = Depends(get_db)) -> ServiceListResponse:
    services = ListActiveServicesUseCase(db).execute()
    return ServiceListResponse(items=[_to_summary(service) for service in services])
