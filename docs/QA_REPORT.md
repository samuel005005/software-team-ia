# QA Report — Barbería App

**Fecha:** 2026-07-08  
**Tareas validadas:** T-001 — T-051  
**Responsable:** Developer (autovalidación técnica pre-QA formal)

## T-051 — Consulta barberos disponibles por servicio y fecha (US-004)

| Criterio SPEC | Estado | Evidencia |
|---------------|--------|-----------|
| Barberos que ofrecen el servicio para la fecha | ✅ | `GET /availability?service_id=&date=` + `ListAvailableBarbersUseCase` |
| No aparecen barberos inactivos | ✅ | `BarberRepository.list_bookable()` filtra `is_active`; tests de exclusión |
| Slots de horario disponibles | ⏳ | Pendiente T-052 (`slots=[]` en respuesta actual) |
| Endpoint público (cliente) | ✅ | Sin auth requerida; alineado a SPEC permisos cliente |
| Fecha pasada rechazada | ✅ | `400` con `InvalidDateError` |
| Servicio inactivo/inexistente | ✅ | `404` con `ServiceNotAvailableError` |
| Respeta horario del local cerrado | ✅ | Retorna lista vacía si `is_closed` |
| Respeta disponibilidad semanal del barbero | ✅ | Filtra por `barber_availability.is_active` |

| Área | Comando | Resultado |
|------|---------|-----------|
| Backend | `pytest` | 93/93 ✅ |
| Flutter | `flutter analyze` + `flutter test` | 50/50 ✅ |

## T-050 — Disponibilidad recurrente del barbero (US-010)

| Criterio SPEC | Estado | Evidencia |
|---------------|--------|-----------|
| Definir bloques de disponibilidad por día de la semana | ✅ | `PATCH /barber/availability` + `BarberAvailabilityPage` |
| Slots fuera de disponibilidad no reservables | ✅ | `ListAvailableBarbersUseCase` filtra por `barber_availability.is_active` |
| Actualizar disponibilidad sin afectar citas confirmadas | ✅ | Patrón recurrente semanal (no fecha específica) |
| Solo barbero accede | ✅ | Test `test_barber_availability_forbidden_for_client` |

| Área | Comando | Resultado |
|------|---------|-----------|
| Backend | `pytest` | 93/93 ✅ |
| Flutter | `flutter analyze` + `flutter test` | 50/50 ✅ |

## T-045 — Configuración del horario del local (US-016)

| Criterio SPEC | Estado | Evidencia |
|---------------|--------|-----------|
| Configurar hora apertura/cierre por día | ✅ | `PATCH /admin/business-hours` + `AdminBusinessHoursPage` |
| Marcar días no laborables (festivos) | ✅ | Campo `is_closed` por weekday |
| No reservar citas fuera del horario del local | ✅ | `ListAvailableBarbersUseCase` retorna vacío si `is_closed`; test `test_availability_returns_empty_when_business_closed` |
| Solo admin accede | ✅ | Test `test_admin_business_hours_forbidden_for_client` |

| Área | Comando | Resultado |
|------|---------|-----------|
| Backend | `pytest` | 87/87 ✅ |
| Flutter | `flutter analyze` + `flutter test` | 48/48 ✅ |

## T-044 — Gestión de clientes desde admin (US-017)

| Criterio SPEC | Estado | Evidencia |
|---------------|--------|-----------|
| Listar clientes registrados | ✅ | `GET /admin/users` |
| Desactivar cuenta de cliente | ✅ | `PATCH /admin/users/{id}` con `is_active: false` |
| Ver citas asociadas a un cliente | ✅ | `GET /admin/users/{id}/appointments` |
| Solo admin accede | ✅ | Test `test_admin_clients_forbidden_for_client` |

| Área | Comando | Resultado |
|------|---------|-----------|
| Backend | `pytest` | 69/69 ✅ |
| Flutter | `flutter analyze` + `flutter test` | 46/46 ✅ |

## T-043 — Asignación servicios por barbero

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| Admin asigna subset de servicios | ✅ | `PUT /admin/barbers/{id}/services` |
| Reemplazo idempotente de asignaciones | ✅ | Test `test_admin_set_barber_services_replaces_existing` |
| Solo servicios activos asignables | ✅ | 400 si servicio inactivo |
| Catálogo filtra por servicio | ✅ | `GET /barbers?service_id=` |

## Veredicto

**APROBADO** — T-051 consulta de barberos disponibles por servicio y fecha (criterio de slots pendiente en T-052).

## Próximo paso

**T-052** — algoritmo de generación de slots reservables (US-004, US-005)
