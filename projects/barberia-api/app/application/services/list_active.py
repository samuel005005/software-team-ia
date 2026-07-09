from sqlalchemy.orm import Session

from app.infrastructure.repositories.service_repository import ServiceRecord, ServiceRepository


class ListActiveServicesUseCase:
    def __init__(self, session: Session) -> None:
        self._services = ServiceRepository(session)

    def execute(self) -> list[ServiceRecord]:
        return self._services.list_active()
