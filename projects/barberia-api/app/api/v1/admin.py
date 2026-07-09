from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.appointments.void_appointment import (
    VoidAppointmentCommand,
    VoidAppointmentUseCase,
)

from app.application.barbers.manage import (
    CreateBarberCommand,
    CreateBarberUseCase,
    ListAllBarbersUseCase,
    UpdateBarberCommand,
    UpdateBarberUseCase,
)
from app.application.barbers.services_assignment import (
    GetBarberServicesUseCase,
    SetBarberServicesCommand,
    SetBarberServicesUseCase,
)
from app.application.clients.manage import (
    ListAllClientsUseCase,
    ListClientAppointmentsUseCase,
    UpdateClientCommand,
    UpdateClientUseCase,
)
from app.application.schedules.business_hours import (
    BusinessHoursDayCommand,
    ListBusinessHoursUseCase,
    UpdateBusinessHoursUseCase,
)
from app.application.services.manage import (
    CreateServiceCommand,
    CreateServiceUseCase,
    ListAllServicesUseCase,
    UpdateServiceCommand,
    UpdateServiceUseCase,
)
from app.core.dependencies.auth import require_admin
from app.core.dependencies.database import get_db
from app.domain.appointments.errors import (
    AppointmentNotCancellableError,
    AppointmentNotFoundError,
)
from app.domain.auth.errors import EmailAlreadyExistsError
from app.domain.barbers.errors import BarberNotFoundError, InvalidServiceAssignmentError
from app.domain.schedules.errors import InvalidBusinessHoursError
from app.domain.services.errors import ServiceNotFoundError
from app.domain.users.errors import ClientNotFoundError
from app.infrastructure.db.models.user import User
from app.schemas.barbers import (
    AdminBarberListResponse,
    AdminBarberSummary,
    BarberCreateRequest,
    BarberServicesAssignmentRequest,
    BarberUpdateRequest,
)
from app.schemas.clients import (
    AdminClientAppointmentListResponse,
    AdminClientAppointmentSummary,
    AdminClientListResponse,
    AdminClientSummary,
    ClientUpdateRequest,
)
from app.schemas.schedules import (
    BusinessHoursDaySummary,
    BusinessHoursListResponse,
    BusinessHoursUpdateRequest,
)
from app.schemas.appointments import AppointmentResponse, VoidAppointmentRequest
from app.schemas.services import (
    ServiceCreateRequest,
    ServiceListResponse,
    ServiceSummary,
    ServiceUpdateRequest,
)

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


@router.get("/services", response_model=ServiceListResponse)
def admin_list_services(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> ServiceListResponse:
    services = ListAllServicesUseCase(db).execute()
    return ServiceListResponse(items=[_to_summary(service) for service in services])


@router.post("/services", response_model=ServiceSummary, status_code=status.HTTP_201_CREATED)
def admin_create_service(
    body: ServiceCreateRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> ServiceSummary:
    use_case = CreateServiceUseCase(db)
    try:
        service = use_case.execute(
            CreateServiceCommand(
                name=body.name,
                description=body.description,
                duration_minutes=body.duration_minutes,
                price_dop=body.price_dop,
                is_active=body.is_active,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    return _to_summary(service)


@router.patch("/services/{service_id}", response_model=ServiceSummary)
def admin_update_service(
    service_id: UUID,
    body: ServiceUpdateRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> ServiceSummary:
    if (
        body.name is None
        and body.description is None
        and body.duration_minutes is None
        and body.price_dop is None
        and body.is_active is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    use_case = UpdateServiceUseCase(db)
    try:
        service = use_case.execute(
            UpdateServiceCommand(
                service_id=service_id,
                name=body.name,
                description=body.description,
                duration_minutes=body.duration_minutes,
                price_dop=body.price_dop,
                is_active=body.is_active,
            )
        )
        db.commit()
    except ServiceNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado",
        ) from exc
    except Exception:
        db.rollback()
        raise

    return _to_summary(service)


def _to_admin_barber(barber) -> AdminBarberSummary:
    return AdminBarberSummary(
        user_id=barber.user_id,
        email=barber.email,
        display_name=barber.display_name,
        bio=barber.bio,
        photo_url=barber.photo_url,
        is_bookable=barber.is_bookable,
        is_active=barber.is_active,
    )


@router.get("/barbers", response_model=AdminBarberListResponse)
def admin_list_barbers(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminBarberListResponse:
    barbers = ListAllBarbersUseCase(db).execute()
    return AdminBarberListResponse(items=[_to_admin_barber(barber) for barber in barbers])


@router.post("/barbers", response_model=AdminBarberSummary, status_code=status.HTTP_201_CREATED)
def admin_create_barber(
    body: BarberCreateRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminBarberSummary:
    use_case = CreateBarberUseCase(db)
    try:
        barber = use_case.execute(
            CreateBarberCommand(
                email=body.email,
                password=body.password,
                display_name=body.display_name,
                bio=body.bio,
                photo_url=body.photo_url,
                is_bookable=body.is_bookable,
            )
        )
        db.commit()
    except EmailAlreadyExistsError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        ) from exc
    except Exception:
        db.rollback()
        raise

    return _to_admin_barber(barber)


@router.patch("/barbers/{user_id}", response_model=AdminBarberSummary)
def admin_update_barber(
    user_id: UUID,
    body: BarberUpdateRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminBarberSummary:
    if (
        body.display_name is None
        and body.bio is None
        and body.photo_url is None
        and body.is_bookable is None
        and body.is_active is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    use_case = UpdateBarberUseCase(db)
    try:
        barber = use_case.execute(
            UpdateBarberCommand(
                user_id=user_id,
                display_name=body.display_name,
                bio=body.bio,
                photo_url=body.photo_url,
                is_bookable=body.is_bookable,
                is_active=body.is_active,
            )
        )
        db.commit()
    except BarberNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Barbero no encontrado",
        ) from exc
    except Exception:
        db.rollback()
        raise

    return _to_admin_barber(barber)


def _to_service_summary(service) -> ServiceSummary:
    return ServiceSummary(
        id=service.id,
        name=service.name,
        description=service.description,
        duration_minutes=service.duration_minutes,
        price_dop=service.price_dop,
        is_active=service.is_active,
    )


@router.get("/barbers/{user_id}/services", response_model=ServiceListResponse)
def admin_get_barber_services(
    user_id: UUID,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> ServiceListResponse:
    use_case = GetBarberServicesUseCase(db)
    try:
        services = use_case.execute(user_id)
    except BarberNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Barbero no encontrado",
        ) from exc

    return ServiceListResponse(items=[_to_service_summary(service) for service in services])


@router.put("/barbers/{user_id}/services", response_model=ServiceListResponse)
def admin_set_barber_services(
    user_id: UUID,
    body: BarberServicesAssignmentRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> ServiceListResponse:
    use_case = SetBarberServicesUseCase(db)
    try:
        services = use_case.execute(
            SetBarberServicesCommand(
                barber_user_id=user_id,
                service_ids=[UUID(str(service_id)) for service_id in body.service_ids],
            )
        )
        db.commit()
    except BarberNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Barbero no encontrado",
        ) from exc
    except InvalidServiceAssignmentError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Servicios inválidos o inactivos",
        ) from exc
    except Exception:
        db.rollback()
        raise

    return ServiceListResponse(items=[_to_service_summary(service) for service in services])


def _to_admin_client(client) -> AdminClientSummary:
    return AdminClientSummary(
        user_id=client.user_id,
        email=client.email,
        full_name=client.full_name,
        phone=client.phone,
        is_active=client.is_active,
    )


def _to_client_appointment(appointment) -> AdminClientAppointmentSummary:
    return AdminClientAppointmentSummary(
        id=appointment.id,
        status=appointment.status,
        scheduled_start=appointment.scheduled_start,
        scheduled_end=appointment.scheduled_end,
        service_name=appointment.service_name,
        barber_display_name=appointment.barber_display_name,
    )


@router.get("/users", response_model=AdminClientListResponse)
def admin_list_users(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminClientListResponse:
    clients = ListAllClientsUseCase(db).execute()
    return AdminClientListResponse(items=[_to_admin_client(client) for client in clients])


@router.patch("/users/{user_id}", response_model=AdminClientSummary)
def admin_update_user(
    user_id: UUID,
    body: ClientUpdateRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminClientSummary:
    if body.is_active is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    use_case = UpdateClientUseCase(db)
    try:
        client = use_case.execute(
            UpdateClientCommand(
                user_id=user_id,
                is_active=body.is_active,
            )
        )
        db.commit()
    except ClientNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        ) from exc
    except Exception:
        db.rollback()
        raise

    return _to_admin_client(client)


@router.get("/users/{user_id}/appointments", response_model=AdminClientAppointmentListResponse)
def admin_list_client_appointments(
    user_id: UUID,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminClientAppointmentListResponse:
    use_case = ListClientAppointmentsUseCase(db)
    try:
        appointments = use_case.execute(user_id)
    except ClientNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        ) from exc

    return AdminClientAppointmentListResponse(
        items=[_to_client_appointment(appointment) for appointment in appointments]
    )


@router.patch(
    "/appointments/{appointment_id}/void",
    response_model=AppointmentResponse,
)
def admin_void_appointment(
    appointment_id: UUID,
    body: VoidAppointmentRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AppointmentResponse:
    use_case = VoidAppointmentUseCase(db)
    try:
        result = use_case.execute(
            VoidAppointmentCommand(
                appointment_id=appointment_id,
                admin_user_id=current_user.id,
                reason=body.reason,
                now=datetime.now(timezone.utc),
            )
        )
        db.commit()
    except AppointmentNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada",
        ) from exc
    except AppointmentNotCancellableError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cita no se puede anular",
        ) from exc
    except Exception:
        db.rollback()
        raise

    return AppointmentResponse(
        id=result.id,
        status=result.status,
        scheduled_start=result.scheduled_start,
        scheduled_end=result.scheduled_end,
        service_id=result.service_id,
        service_name=result.service_name,
        barber_user_id=result.barber_user_id,
        barber_display_name=result.barber_display_name,
    )


def _to_business_hours_summary(record) -> BusinessHoursDaySummary:
    return BusinessHoursDaySummary(
        weekday=record.weekday,
        open_time=record.open_time,
        close_time=record.close_time,
        is_closed=record.is_closed,
    )


@router.get("/business-hours", response_model=BusinessHoursListResponse)
def admin_list_business_hours(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> BusinessHoursListResponse:
    records = ListBusinessHoursUseCase(db).execute()
    return BusinessHoursListResponse(
        items=[_to_business_hours_summary(record) for record in records]
    )


@router.patch("/business-hours", response_model=BusinessHoursListResponse)
def admin_update_business_hours(
    body: BusinessHoursUpdateRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> BusinessHoursListResponse:
    use_case = UpdateBusinessHoursUseCase(db)
    try:
        records = use_case.execute(
            [
                BusinessHoursDayCommand(
                    weekday=item.weekday,
                    open_time=item.open_time,
                    close_time=item.close_time,
                    is_closed=item.is_closed,
                )
                for item in body.items
            ]
        )
        db.commit()
    except InvalidBusinessHoursError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception:
        db.rollback()
        raise

    return BusinessHoursListResponse(
        items=[_to_business_hours_summary(record) for record in records]
    )
