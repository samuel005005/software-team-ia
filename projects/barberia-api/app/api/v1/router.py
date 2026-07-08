from fastapi import APIRouter

from app.api.v1 import (
    admin,
    appointments,
    auth,
    availability,
    barbers,
    health,
    services,
    users,
)

v1_router = APIRouter()

v1_router.include_router(health.router, tags=["health"])
v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
v1_router.include_router(users.router, tags=["users"])
v1_router.include_router(barbers.router, prefix="/barbers", tags=["barbers"])
v1_router.include_router(services.router, prefix="/services", tags=["services"])
v1_router.include_router(availability.router, prefix="/availability", tags=["availability"])
v1_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
v1_router.include_router(admin.router, prefix="/admin", tags=["admin"])
