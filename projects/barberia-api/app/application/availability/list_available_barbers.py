from datetime import date
import uuid

from sqlalchemy.orm import Session

from app.domain.availability.errors import InvalidDateError, ServiceNotAvailableError
from app.domain.availability.scheduling import date_to_weekday
from app.infrastructure.repositories.barber_repository import BarberPublicProfile, BarberRepository
from app.infrastructure.repositories.schedule_repository import ScheduleRepository
from app.infrastructure.repositories.service_repository import ServiceRepository


class ListAvailableBarbersUseCase:
    def __init__(self, session: Session) -> None:
        self._services = ServiceRepository(session)
        self._barbers = BarberRepository(session)
        self._schedule = ScheduleRepository(session)

    def execute(self, service_id: uuid.UUID, target_date: date) -> list[BarberPublicProfile]:
        if target_date < date.today():
            raise InvalidDateError("La fecha no puede estar en el pasado")

        service = self._services.get_by_id(service_id)
        if service is None or not service.is_active:
            raise ServiceNotAvailableError("Servicio no disponible")

        weekday = date_to_weekday(target_date)
        business_hours = self._schedule.get_business_hours(weekday)
        if business_hours is not None and business_hours.is_closed:
            return []

        available_barber_ids = self._schedule.barber_ids_with_availability_on_weekday(weekday)
        if not available_barber_ids:
            return []

        bookable_barbers = self._barbers.list_bookable(service_id=service_id)
        return [
            barber
            for barber in bookable_barbers
            if uuid.UUID(barber.user_id) in available_barber_ids
        ]
