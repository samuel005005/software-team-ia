# Plan de tareas — Barbería App

> Documento vivo. Gestionado por **Architect** (creación) y **Developer** (progreso).  
> Enfoque: MVP mobile-first con backend REST separado.

## Leyenda

- `[ ]` Pendiente
- `[~]` En progreso
- `[x]` Completada
- `[!]` Bloqueada

## Decisión arquitectónica base

- Se reutiliza `projects/barberia-app/` como bootstrap Flutter.
- Se migra la estructura interna a una arquitectura modular.
- El backend REST vive en `projects/barberia-api/` (FastAPI modular).

---

## Fase 1 — Setup y base técnica

| ID | Tarea | Responsable | Estado |
|----|-------|-------------|--------|
| T-001 | Reestructurar `projects/barberia-app/lib/` con Clean Architecture (`app/`, `core/`, `shared/`, `features/` con capas `domain/data/application/presentation`) | Developer | `[x]` |
| T-002 | Configurar navegación base con rutas autenticadas y públicas | Developer | `[x]` |
| T-003 | Configurar estado global y providers base | Developer | `[x]` |
| T-004 | Configurar cliente HTTP, manejo de errores e interceptores de auth | Developer | `[x]` |
| T-005 | Configurar almacenamiento seguro de sesión | Developer | `[x]` |
| T-006 | Crear esqueleto del backend REST y estructura modular inicial | Developer | `[x]` |
| T-007 | Configurar conexión a PostgreSQL y migraciones iniciales | Developer | `[x]` |
| T-008 | Definir enums, schemas y contratos base del dominio | Developer | `[x]` |

### T-001 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Requisitos SPEC:** Base técnica para todas las historias MVP (sin funcionalidad aún).

**Archivos clave creados:**
- `core/application/use_case.dart` — contrato base de casos de uso
- `core/utils/result.dart` — `Result<T>` (Success/Error)
- `core/error/failures.dart`, `exception_mapper.dart` — fallos de dominio
- `core/network/dio_exception_mapper.dart`, `dio_safe_caller.dart` — adaptador HTTP
- `app/presentation/pages/bootstrap_page.dart` — pantalla bootstrap sin negocio
- Features: `auth`, `appointments`, `services`, `client_booking`, `barber_schedule`, `profile` con capas `domain/data/application/presentation`

**Decisiones:**
- Capa `application/` separada de `domain/` para casos de uso (Clean Architecture)
- Solo ruta `/` activa; rutas de negocio definidas como constantes para T-002
- Sin pantallas placeholder de login/citas (evitar mezclar con funcionalidad futura)
- `Result<T>` + `Failure` en lugar de excepciones en dominio/aplicación
- Interceptores de auth diferidos a T-004

**Riesgos:**
- `ARCHITECTURE.md` aún documenta estructura sin capa `application/` — actualizar en revisión Architect
- GoRouter sin guards hasta T-002

**Validación:** `flutter analyze` ✅ · `flutter test` (10 tests) ✅

### T-002 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Requisitos SPEC:** Soporte de roles Cliente, Barbero, Administrador (navegación por rol).

**Archivos clave:**
- `core/navigation/` — `UserRole`, `AuthSession`, `SessionNotifier` (en memoria)
- `app/router/router_redirect.dart` — guards y redirección por rol (función pura testeable)
- `app/router/router_refresh_notifier.dart` — GoRouter reactivo a sesión
- `app/presentation/shells/authenticated_shell.dart` — shell con bottom nav por rol
- Rutas públicas: `/login`, `/register`
- Rutas protegidas: cliente, barbero, admin (alineadas a ARCHITECTURE.md)
- `features/auth/presentation/pages/login_page.dart` — acceso temporal por rol (sin API)

**Decisiones:**
- Sesión en memoria para T-002; persistencia segura en T-005
- `RouterRedirect` como lógica pura (Strategy) desacoplada de GoRouter
- Login temporal con botones por rol solo para validar navegación
- `ShellRoute` + `AuthenticatedShell` para área autenticada

**Riesgos:**
- Login mock no debe llegar a producción sin reemplazo (T-030+)
- T-003 ampliará providers globales; T-004 añadirá interceptores HTTP

**Validación:** `flutter analyze` ✅ · `flutter test` (18 tests) ✅

### T-003 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Requisitos SPEC:** Preparar estado global transversal para configuración UI y bootstrap.

**Archivos clave:**
- `app/state/app_state.dart` — estado global inmutable (`themeMode`, `locale`, `isInitialized`, `isGlobalLoading`)
- `app/providers/app_state_providers.dart` — `AppStateNotifier` + providers derivados
- `app/app.dart` — integración de `themeMode`, `locale`, `darkTheme`
- `app/theme/app_theme.dart` — tema oscuro base
- `features/auth/presentation/pages/login_page.dart` — consumo de providers globales (loading + cambio de tema)

**Decisiones:**
- Estado global centralizado en `appStateProvider` (single source of truth UI)
- Providers derivados (`themeModeProvider`, `appLocaleProvider`, etc.) para bajo acoplamiento
- Flags globales base sin mezclar lógica de negocio
- Persistencia de preferencias diferida (se conectará con storage en T-005)

**Riesgos:**
- Estado aún en memoria; reinicios no conservan preferencias
- `isInitialized` se marca desde login temporal y se reemplazará con bootstrap real en auth

**Validación:** `flutter analyze` ✅ · `flutter test` (21 tests) ✅

### T-004 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Requisitos SPEC:** Base HTTP segura para autenticación JWT y consumo API (F-C01, F-C02, roles).

**Archivos clave:**
- `core/network/contracts/auth_token_provider.dart` — contrato de tokens
- `core/network/auth_token_store.dart` — almacén en memoria (T-005: secure storage)
- `core/network/api_client_factory.dart` — factory con interceptores
- `core/network/interceptors/auth_interceptor.dart` — header Bearer
- `core/network/interceptors/unauthorized_interceptor.dart` — manejo 401
- `core/network/interceptors/error_mapping_interceptor.dart` — mapeo de errores
- `core/network/remote_data_source.dart` — base `execute()` con `Result<T>`
- `core/providers/network_providers.dart` — wiring Riverpod

**Decisiones:**
- Interceptores en orden: Auth → Unauthorized → ErrorMapping → Logging
- Rutas públicas `/auth/login`, `/auth/register`, `/auth/refresh` sin token
- Refresh token real diferido a T-031; en 401 se limpia sesión
- Login mock asigna tokens temporales para validar interceptor

**Riesgos:**
- Tokens en memoria se pierden al reiniciar app (T-005)
- Retry automático tras refresh no implementado aún

**Validación:** `flutter analyze` ✅ · `flutter test` (29 tests) ✅

### T-005 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Requisitos SPEC:** F-C01, F-C02 — sesión segura con JWT (base local).

**Archivos clave:**
- `core/storage/secure_storage_service.dart` — contrato de storage
- `core/storage/flutter_secure_storage_service.dart` — implementación producción
- `core/storage/session_persistence.dart` — persistencia tokens + rol
- `core/providers/session_bootstrap_provider.dart` — restauración al iniciar
- `core/navigation/session_notifier.dart` — signIn/signOut con persistencia
- Dependencia: `flutter_secure_storage`

**Decisiones:**
- Tokens y rol en secure storage (no SharedPreferences)
- Bootstrap async antes de renderizar `MaterialApp.router`
- `InMemorySecureStorageService` para tests
- Refresh token API diferido a T-031

**Documentación actualizada:**
- `docs/ARCHITECTURE.md` — estructura real T-001..T-005 y capa `application/`

**Riesgos:**
- En web, secure storage tiene limitaciones de plataforma
- Login mock sigue activo hasta Fase 3 (T-030+)

**Validación:** `flutter analyze` ✅ · `flutter test` (33 tests) ✅

### T-006 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Requisitos SPEC:** Base API REST para todas las historias MVP.

**Proyecto:** `projects/barberia-api/`

**Archivos clave:**
- `app/main.py` — FastAPI + CORS + `/health`
- `app/api/v1/` — routers stub (auth, users, barbers, services, availability, appointments, admin)
- `app/core/config.py` — settings con pydantic-settings
- Capas vacías: `application/`, `infrastructure/repositories/`, `infrastructure/security/`

**Decisiones:**
- Endpoints de negocio retornan `501 Not Implemented` hasta Fase 2/3
- Prefijo API: `/api/v1`
- OpenAPI automático en `/docs`

**Validación:** `pytest` (8 tests) ✅

### T-007 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Requisitos SPEC:** Persistencia PostgreSQL (preparación).

**Archivos clave:**
- `app/infrastructure/db/base.py`, `session.py` — SQLAlchemy 2.x
- `alembic/` — migraciones (`0001_initial` placeholder)
- `docker-compose.yml` — PostgreSQL 15 local
- `.env.example` — `DATABASE_URL`

**Decisiones:**
- Migración inicial vacía; tablas en T-020+
- `get_db()` dependency lista para Fase 2

**Riesgos:**
- Requiere PostgreSQL corriendo para `alembic upgrade` en entorno real

**Validación:** `pytest` ✅ · estructura Alembic verificada

### T-008 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Requisitos SPEC:** RN-04 (estados de cita), roles de usuario.

**Archivos clave:**
- `app/domain/enums.py` — `UserRole`, `AppointmentStatus`, `Weekday`
- `app/domain/contracts.py` — `Repository` base
- `app/schemas/` — DTOs Pydantic (auth, users, services, appointments, etc.)

**Decisiones:**
- `AppointmentStatus` incluye `pendiente` (SPEC) y estados de ARCHITECTURE
- Schemas separados por dominio HTTP; no exponer entidades aún

**Validación:** `tests/test_domain_enums.py` ✅

### T-020 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Migración:** `0002_domain_tables` (users, client_profiles, barber_profiles)

**Modelos:** `app/infrastructure/db/models/user.py`, `client_profile.py`, `barber_profile.py`

**Decisiones:**
- UUID como PK en `users`
- `client_profiles` / `barber_profiles` con FK CASCADE a `users`
- Enum PostgreSQL `user_role` con valores `client|barber|admin`

### T-021 — Notas (2026-07-08)

**Migración:** `0002_domain_tables` (services, barber_services)  
**Constraint:** `UNIQUE(barber_user_id, service_id)`

### T-022 — Notas (2026-07-08)

**Migración:** `0002_domain_tables` (business_hours, barber_availability)  
**Constraint:** `weekday` entre 1 y 7

### T-023 — Notas (2026-07-08)

**Migración:** `0002_domain_tables` (appointments, appointment_status_history, audit_logs)  
**Enum:** `appointment_status` alineado a SPEC + ARCHITECTURE

### T-024 — Notas (2026-07-08)

**Migración:** `0003_appointment_constraints`  
**Constraint:** `EXCLUDE USING gist` anti-solapamiento por barbero (excluye `cancelada`)  
**Extensión:** `btree_gist`

### T-025 — Notas (2026-07-08)

**Dominio:** `app/domain/appointments/scheduling.py` → `calculate_scheduled_end()`  
**DB:** `CHECK (scheduled_end > scheduled_start)`  
**Tests:** `test_appointments_constraints.py`

**Validación Fase 2:** `alembic upgrade head` ✅ · `pytest` (13 tests) ✅

### T-030 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historia:** US-001 — Registro de cuenta cliente

**Archivos clave:**
- `app/application/auth/register_client.py` — `RegisterClientUseCase`
- `app/infrastructure/repositories/user_repository.py`
- `app/infrastructure/security/password_hasher.py` — bcrypt
- `app/api/v1/auth.py` — `POST /api/v1/auth/register` → `201`
- `app/schemas/auth.py` — `RegisterResponse`

**Criterios SPEC cubiertos:**
- Email único + contraseña mín. 8 caracteres
- `409 Conflict` si email duplicado
- Crea `User` (rol `client`) + `ClientProfile`
- Password almacenado como hash bcrypt (nunca en claro)

**Decisiones:**
- Email normalizado a minúsculas
- Sin JWT en registro (login en T-031)
- `bcrypt` directo (passlib incompatible con Python 3.14)

**Validación:** `pytest` (20 tests) ✅

### T-031 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historia:** US-002 — Inicio de sesión

**Archivos clave:**
- `app/application/auth/login.py` — `LoginUseCase`, `RefreshSessionUseCase`
- `app/infrastructure/security/jwt_service.py` — access JWT (HS256)
- `app/infrastructure/repositories/refresh_token_repository.py`
- `app/infrastructure/db/models/refresh_token.py`
- Migración `0004_refresh_tokens`

**Endpoints:**
- `POST /api/v1/auth/login` → `TokenResponse` (`200`)
- `POST /api/v1/auth/refresh` → rota refresh token (`200`)

**Decisiones:**
- Access token JWT: `sub`, `email`, `role`, `type=access`, exp 30 min
- Refresh token opaco (SHA-256 en DB), rotación en cada refresh
- `401` credenciales/refresh inválidos; `403` cuenta inactiva
- Mensaje genérico en login fallido (no revelar si email existe)

**Validación:** `pytest` (28 tests) ✅

### T-032 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historias:** US-001, US-002 — Login/registro Flutter con API real

**Archivos clave:**
- `features/auth/domain/` — `AuthRepository`, `LoginUseCase`, `RegisterUseCase`
- `features/auth/data/` — DTOs, `AuthRemoteDataSource`, `AuthRepositoryImpl`
- `features/auth/presentation/pages/login_page.dart` — formulario email/contraseña
- `features/auth/presentation/pages/register_page.dart` — registro cliente
- `core/utils/jwt_decoder.dart` — extrae rol del access token
- `core/providers/network_providers.dart` — refresh token real en interceptor

**Decisiones:**
- API dev: `http://127.0.0.1:8001/api/v1`
- `authDioProvider` separado para evitar ciclo con interceptores
- Botones mock barbero/admin solo en `kDebugMode`
- Tras registro exitoso → snackbar + navegación a login

**Validación:** `flutter analyze` ✅ · `flutter test` (35 tests) ✅

### T-033 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historia:** US-008 — Editar perfil personal (cliente)

**Backend:**
- `GET /api/v1/me` — perfil autenticado (JWT Bearer)
- `PATCH /api/v1/me` — actualizar `full_name` y `phone` (solo clientes)
- `app/core/dependencies/auth.py` — `get_current_user`, `require_client`
- `UpdateClientProfileUseCase`

**Flutter:**
- Feature `profile/` — repository, use cases, `ProfilePage` / `ClientProfilePage`
- Email solo lectura (MVP)
- Barbero/admin: mensaje placeholder (T-034) → **T-034 completada:** `BarberProfilePage`

**Validación:** `pytest` (32) ✅ · `flutter test` (35) ✅

### T-034 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historia:** US-009 — Editar perfil profesional (barbero)

**Backend:**
- `GET/PATCH /api/v1/me` — barberos editan `full_name` (display_name), `bio`, `photo_url`
- `UpdateMyProfileUseCase` unificado por rol (cliente / barbero)
- `GET /api/v1/barbers` — lista barberos bookables activos (público)
- `BarberRepository.list_bookable()`

**Flutter:**
- `UserProfile` + DTOs con `bio` y `photoUrl`
- `BarberProfilePage` — formulario nombre, descripción y URL de foto
- `ProfilePage` enruta por rol desde `myProfileProvider`

**Validación:** `pytest` (37) ✅ · `flutter test` (35) ✅

### T-035 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historia:** US-002 — Guards de acceso por rol

**Backend:**
- `require_roles`, `require_client`, `require_barber`, `require_admin`
- `/admin/*` — solo admin (401 sin token, 403 rol incorrecto)
- `/appointments` POST/cancel — solo cliente; GET — autenticado
- `/barber/*` — stubs protegidos solo barbero

**Flutter:**
- `RouterRedirect.canAccess()` — matriz explícita por rol/ruta
- `AppRoutes.clientOnlyRoutes`, `sharedRoutes`
- Tests ampliados (barbero/admin no cruzan áreas)

**Validación:** `pytest` (48) ✅ · `flutter test` (41) ✅

### T-040 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historia:** US-003 — Ver servicios disponibles

**Backend:**
- `GET /api/v1/services` — servicios activos ordenados alfabéticamente
- `ServiceRepository.list_active()` + `ListActiveServicesUseCase`
- Endpoint público (sin auth)

**Flutter:**
- Feature `services/` — repository, use case, `ServicesPage`
- Lista con nombre, duración, precio (RD$) y descripción opcional
- Ruta `/services` conectada a pantalla real

**Validación:** `pytest` (50) ✅ · `flutter test` (43) ✅

### T-041 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historia:** US-015 — Gestionar servicios (admin)

**Backend:**
- `GET/POST /api/v1/admin/services` — listar (incl. inactivos) y crear
- `PATCH /api/v1/admin/services/{id}` — editar y activar/desactivar
- `CreateServiceUseCase`, `UpdateServiceUseCase`, `ListAllServicesUseCase`
- Solo admin (`require_admin`)

**Flutter:**
- Feature `admin/services/` — `AdminServicesPage` + formulario dialog
- Crear, editar y toggle activo desde `/admin/services`

**Validación:** `pytest` (55) ✅ · `flutter test` (45) ✅

### T-042 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historia:** US-014 — Gestionar barberos (admin)

**Backend:**
- `GET/POST /api/v1/admin/barbers` — listar y crear con credenciales
- `PATCH /api/v1/admin/barbers/{user_id}` — editar, activar/desactivar, bookable
- `CreateBarberUseCase`, `UpdateBarberUseCase`, `ListAllBarbersUseCase`
- Desactivación soft (`is_active`); sin delete físico

**Flutter:**
- Feature `admin/barbers/` — `AdminBarbersPage` + formulario
- Tab **Barberos** en navegación admin
- Toggle activo/reservable desde lista

**Validación:** `pytest` (60) ✅ · `flutter test` (46) ✅

### T-043 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historia:** US-014 — Asignación servicios por barbero

**Backend:**
- `GET/PUT /api/v1/admin/barbers/{user_id}/services` — consultar y reemplazar asignaciones
- Tabla `barber_services` vía `BarberServiceRepository`
- `GET /api/v1/barbers?service_id=` — filtra barberos que ofrecen el servicio
- Solo servicios activos asignables

**Flutter:**
- `AdminBarberServicesDialog` — multi-select de servicios activos
- Botón **Asignar servicios** en cada barbero admin

**Validación:** `pytest` (64) ✅ · `flutter test` (46) ✅

### T-044 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historia:** US-017 — Gestionar usuarios (clientes)

**Backend:**
- `GET /api/v1/admin/users` — listar clientes registrados
- `PATCH /api/v1/admin/users/{id}` — desactivar/reactivar cuenta (`is_active`)
- `GET /api/v1/admin/users/{id}/appointments` — citas asociadas al cliente
- `ClientRepository`, `AppointmentRepository`, use cases en `application/clients/`

**Flutter:**
- Feature `admin/users/` — `AdminUsersPage` con lista de clientes
- Toggle activo/inactivo y diálogo de citas por cliente
- Ruta `/admin/users` conectada en `app_router.dart`

**Validación:** `pytest` (69) ✅ · `flutter test` (46) ✅

### T-045 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historia:** US-016 — Configurar horarios del local

**Backend:**
- `GET/PATCH /api/v1/admin/business-hours` — consultar y reemplazar horario semanal
- `ListBusinessHoursUseCase`, `UpdateBusinessHoursUseCase` en `application/schedules/`
- Validación de dominio: weekday 1-7, apertura < cierre, días únicos
- Integración con disponibilidad: días `is_closed` excluyen barberos (`ListAvailableBarbersUseCase`)

**Flutter:**
- Feature `admin/business_hours/` — `AdminBusinessHoursPage` con edición por día
- Toggle **Día cerrado** + selectores de apertura/cierre
- Ruta `/admin/business-hours` conectada en `app_router.dart` y navegación admin

**Validación:** `pytest` (87) ✅ · `flutter analyze` ✅ · `flutter test` (48) ✅

### T-050 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historia:** US-010 — Definir disponibilidad

**Backend:**
- `GET/PATCH /api/v1/barber/availability` — consultar y reemplazar bloques semanales
- `ListMyBarberAvailabilityUseCase`, `UpdateMyBarberAvailabilityUseCase`
- Validación de dominio: weekday 1-7, inicio < fin cuando `is_active`
- `ScheduleRepository.list_barber_availability()` / `replace_barber_availability()`
- Solo barbero autenticado (`require_barber`); aislado por `barber_user_id`

**Flutter:**
- Feature `barber_schedule/` — repository, use cases, `BarberAvailabilityPage`
- Edición por día con toggle **Disponible** + selectores inicio/fin
- Ruta `/barber/availability` conectada en `app_router.dart`

**Criterios SPEC cubiertos:**
- Bloques de disponibilidad por día de la semana (F-B02)
- Slots fuera de disponibilidad no reservables (RN-05, integrado en `ListAvailableBarbersUseCase`)
- Actualizar disponibilidad no afecta citas existentes (patrón recurrente semanal)

**Validación:** `pytest` (93) ✅ · `flutter analyze` ✅ · `flutter test` (50) ✅

### T-051 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historia:** US-004 — Consultar barberos y disponibilidad

**Backend:**
- `GET /api/v1/availability?service_id=&date=` — barberos disponibles para servicio y fecha
- `ListAvailableBarbersUseCase` — filtra por servicio activo, asignación, bookable, disponibilidad semanal y horario del local
- Filtro opcional `barber_id` para acotar a un barbero
- `slots=[]` reservado para T-052 (generación de slots)

**Dominio:**
- `date_to_weekday()` — mapeo fecha → weekday (1=lunes … 7=domingo)
- `InvalidDateError`, `ServiceNotAvailableError`

**Criterios SPEC cubiertos (parcial US-004):**
- Barberos que ofrecen el servicio seleccionado para la fecha ✅
- No aparecen barberos inactivos ni no reservables ✅
- Slots de horario → T-052

**Validación:** `pytest` (93) ✅ · `flutter analyze` ✅ · `flutter test` (50) ✅

### T-052 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historias:** US-004, US-005 (generación de slots; reserva completa en T-053/T-054)

**Backend:**
- `GetAvailabilityUseCase` — orquesta barberos disponibles (T-051) + generación de slots
- Dominio `app/domain/availability/slots.py` — intersección de ventanas, candidatos, filtro RN-01/RN-06
- Granularidad fija 15 min (`SLOT_STEP_MINUTES`); duración del slot = `service.duration_minutes`
- `Settings.business_timezone` (`America/Santo_Domingo`) para combinar fecha+hora y filtrar slots pasados
- `ScheduleRepository.get_barber_availability_for_weekday()` — bloque activo del barbero
- `AppointmentRepository.list_blocking_for_barber_on_date()` — citas ≠ `cancelada` que intersectan el día
- `GET /availability` retorna `slots` con `start`, `end`, `barber_user_id`

**Criterios SPEC cubiertos (US-004):**
- Slots de horario disponibles (no ocupados) ✅
- Excluye citas activas; `cancelada` no bloquea ✅
- Intersección barbero ∩ horario del local (RN-05) ✅
- Slots pasados excluidos si `date == hoy` ✅
- Barberos inactivos / servicio inactivo — heredado de T-051 ✅

**Validación:** `pytest` (114) ✅

### T-053 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historia:** US-005 — Reservar cita (backend; UI en T-054)

**Backend:**
- `CreateAppointmentUseCase` — creación transaccional con pre-validación de slot, `SELECT FOR UPDATE` y constraint EXCLUDE
- `app/domain/appointments/validation.py` — `is_bookable_slot()` reutiliza lógica T-052 (RN-01, RN-05, RN-06)
- `app/domain/appointments/errors.py` — errores de dominio (pasado, slot ocupado, barbero/servicio no disponible)
- `POST /api/v1/appointments` — `201 Created`, estado inicial `confirmada` (ADR #6)
- `AppointmentResponse` enriquecido — resumen con servicio, barbero, `scheduled_start`/`scheduled_end`
- `AppointmentRepository.create()` + `lock_blocking_for_barber_in_range()`
- `BarberServiceRepository.is_assigned()` — validación RN-10

**Criterios SPEC cubiertos (US-005 — backend):**
- Validación RN-01 (slot no ocupado) ✅
- Estado `confirmada` automática ✅
- Confirmación API con resumen ✅
- Rechazo de reservas en el pasado ✅
- Flujo completo servicio→barbero→fecha/hora→confirmar → T-054 (Flutter)

**Validación:** `pytest` (121) ✅

### T-054 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historias:** US-004 — Consultar barberos y disponibilidad · US-005 — Reservar cita

**Flutter (`projects/barberia-app/`):**
- Feature `client_booking/` — capas domain/data/presentation con wizard de 4 pasos
- `BookAppointmentPage` en `/book-appointment` — servicio → barbero → fecha/hora → confirmar
- Integración `GET /barbers`, `GET /availability`, `POST /appointments`
- Pantalla de confirmación post-reserva con resumen (`confirmada`)
- CTA «Reservar» en `ServicesPage` con pre-selección vía `?serviceId=`
- Manejo UX: slot ocupado (`409` + refresco), sin disponibilidad (empty state), fecha mínima hoy
- Dependencias: `intl`, `flutter_localizations` (formato es-DO)
- Tests: `booking_dtos_test.dart`, `book_appointment_page_test.dart`

**Criterios SPEC cubiertos:**
- US-004: barberos por servicio, slots no ocupados, sin inactivos (API) ✅
- US-005: flujo completo, validación RN-01 vía API, estado `confirmada`, resumen, sin pasado ✅

**Validación:** `flutter analyze` ✅ · `flutter test` (57) ✅

---

## Fase 2 — Dominio y modelo de datos

| ID | Tarea | Historia | Responsable | Estado |
|----|-------|----------|-------------|--------|
| T-020 | Crear tablas `users`, `client_profiles`, `barber_profiles` | US-001, US-002, US-009 | Developer | `[x]` |
| T-021 | Crear tablas `services`, `barber_services` | US-003, US-015 | Developer | `[x]` |
| T-022 | Crear tablas `business_hours`, `barber_availability` | US-010, US-016 | Developer | `[x]` |
| T-023 | Crear tablas `appointments`, `appointment_status_history`, `audit_logs` | US-005, US-006, US-012, US-019 | Developer | `[x]` |
| T-024 | Implementar restricciones para evitar doble reserva | US-005 | Developer | `[x]` |
| T-025 | Implementar lógica de duración por servicio y cálculo de `scheduled_end` | US-003, US-005 | Developer | `[x]` |

---

## Fase 3 — Autenticación y perfil

| ID | Tarea | Historia | Responsable | Estado |
|----|-------|----------|-------------|--------|
| T-030 | Implementar registro cliente en backend | US-001 | Developer | `[x]` |
| T-031 | Implementar login y refresh token | US-002 | Developer | `[x]` |
| T-032 | Implementar pantalla de login/registro Flutter | US-001, US-002 | Developer | `[x]` |
| T-033 | Implementar perfil cliente editable | US-008 | Developer | `[x]` |
| T-034 | Implementar perfil profesional del barbero | US-009 | Developer | `[x]` |
| T-035 | Implementar guards de acceso por rol | US-002 | Developer | `[x]` |

---

## Fase 4 — Catálogo y configuración operativa

| ID | Tarea | Historia | Responsable | Estado |
|----|-------|----------|-------------|--------|
| T-040 | Implementar API y pantallas para listar servicios activos | US-003 | Developer | `[x]` |
| T-041 | Implementar CRUD admin de servicios | US-015 | Developer | `[x]` |
| T-042 | Implementar CRUD admin de barberos | US-014 | Developer | `[x]` |
| T-043 | Implementar asignación de servicios por barbero | US-014, regla de negocio servicios por barbero | Developer | `[x]` |
| T-044 | Implementar gestión de clientes desde admin | US-017 | Developer | `[x]` |
| T-045 | Implementar configuración del horario del local | US-016 | Developer | `[x]` |

---

## Fase 5 — Disponibilidad y reservas

| ID | Tarea | Historia | Responsable | Estado |
|----|-------|----------|-------------|--------|
| T-050 | Implementar disponibilidad recurrente del barbero | US-010 | Developer | `[x]` |
| T-051 | Implementar consulta de barberos disponibles por servicio y fecha | US-004 | Developer | `[x]` |
| T-052 | Implementar algoritmo de generación de slots reservables | US-004, US-005 | Developer | `[x]` |
| T-053 | Implementar creación transaccional de citas con confirmación automática | US-005 | Developer | `[x]` |
| T-054 | Implementar pantalla Flutter de reserva de cita | US-004, US-005 | Developer | `[x]` |
| T-055 | Implementar historial de citas del cliente | US-007 | Developer | `[x]` |
| T-056 | Implementar cancelación con regla de 2 horas | US-006 | Developer | `[x]` |

### T-056 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historia:** US-006 — Cancelar cita

**Backend (`projects/barberia-api/`):**
- `PATCH /api/v1/appointments/{id}/cancel` operativo (reemplaza stub `501`)
- `CancelAppointmentUseCase` con validaciones RN-07 (propiedad), RN-08 (ventana 2 h), RN-09 (estados cancelables)
- `cancellation.py` — política de dominio `is_client_cancellable_status`, `meets_cancellation_notice`
- `cancellation_notice_hours = 2` en `Settings` (configurable vía env)
- `AppointmentRepository.get_by_id()` / `cancel()` — persistencia `status=cancelada`, `cancelled_at`
- Slot liberado vía constraint EXCLUDE existente (sin borrado físico)
- Tests: `test_cancel_appointment.py` (auth, reglas, borde 2 h, integración disponibilidad) · `test_role_guards.py` actualizado

**Flutter (`projects/barberia-app/`):**
- `CancelAppointmentUseCase` + `cancelAppointment()` en datasource/repository
- `AppointmentSummary.canBeCancelledByClient()` — pre-check UI (2 h, estados `pendiente`/`confirmada`)
- `AppointmentTile` — botón «Cancelar cita», diálogo confirmación, snackbar éxito, invalidate lista
- Tests: `cancel_appointment_test.dart` (elegibilidad, DTO, widget, flujo diálogo)

**Criterios SPEC cubiertos:**
- US-006: solo mis citas `pendiente`/`confirmada` ✅ · ventana 2 h (RN-08) ✅ · slot libre ✅ · confirmación UI ✅

**Validación:** `pytest` (146) ✅ · `flutter analyze` ✅ · `flutter test` (70) ✅

### T-055 — Notas de implementación (2026-07-08)

**Estado:** Completada  
**Historia:** US-007 — Ver historial de citas

**Backend (`projects/barberia-api/`):**
- `GET /api/v1/appointments` operativo con `require_client` (reemplaza stub `501`)
- `ListMyAppointmentsUseCase` + `sort_client_appointments()` — futuras primero (asc), pasadas después (desc)
- `ClientAppointmentRecord` extendido con `service_id` y `barber_user_id`
- Ordenamiento aplicado también en listado admin (`ListClientAppointmentsUseCase`)
- Tests: `test_list_my_appointments.py` (auth, aislamiento, campos, orden) · `test_role_guards.py` actualizado

**Flutter (`projects/barberia-app/`):**
- Feature `appointments/` — domain/data/presentation con `AppointmentsPage` en `/appointments`
- Secciones «Próximas» y «Pasadas» con tiles (fecha, servicio, barbero, estado)
- Empty state + CTA reservar · loading/error con reintentar · pull-to-refresh
- Tests: `appointment_dtos_test.dart`, `appointments_page_test.dart`

**Criterios SPEC cubiertos:**
- US-007: listado con fecha/servicio/barbero/estado ✅ · distinción futuras/pasadas ✅ · orden próximas primero ✅

**Validación:** `pytest` (list + guards + create) ✅ · `flutter analyze` ✅ · `flutter test` (61) ✅

---

## Fase 6 — Agenda del barbero y operación diaria

| ID | Tarea | Historia | Responsable | Estado |
|----|-------|----------|-------------|--------|
| T-060 | Implementar endpoint de agenda diaria/semanal del barbero | US-011 | Developer | `[x]` |
| T-061 | Implementar pantalla Flutter de agenda del barbero | US-011 | Developer | `[x]` |
| T-062 | Implementar cambios de estado de cita (`confirmada`, `en_progreso`, `completada`, `no_show`) | US-012 | Developer | `[x]` |
| T-063 | Registrar historial de cambios de estado | US-012 | Developer | `[x]` |
| T-064 | Implementar anulación de cita por admin con motivo | US-019 | Developer | `[x]` |

### T-060 — Notas de implementación (2026-07-09)

**Estado:** Completada  
**Historia:** US-011 — Ver agenda diaria (backend)

**Backend (`projects/barberia-api/`):**
- `GET /api/v1/barber/schedule` operativo bajo `require_barber`
- Query `date` (default: hoy en `business_timezone`) y `end_date` opcional (rango ≤ 7 días)
- `ListMyBarberScheduleUseCase` + `InvalidScheduleRangeError` — validación de rango
- `BarberAppointmentRecord` + `list_by_barber_for_date_range()` — join `Service` + `ClientProfile`, orden ASC por `scheduled_start`
- DTOs `BarberScheduleResponse` / `BarberScheduleAppointmentResponse` con `client_display_name`
- Incluye todos los estados (incl. `cancelada`); aislamiento por `barber_user_id`
- Tests: `test_barber_schedule.py` (13 casos) · `test_role_guards.py` actualizado

**Criterios SPEC cubiertos (backend):**
- US-011: hora, cliente, servicio y estado en respuesta ✅ · orden cronológico ✅ · contrato HTTP para navegar por fecha (UI en T-061) ✅

**Validación:** `pytest` (159) ✅

**Siguiente tarea:** T-062 — cambios de estado de cita en agenda del barbero

### T-061 — Notas de implementación (2026-07-09)

**Estado:** Completada  
**Historia:** US-011 — Ver agenda diaria (Flutter)

**Flutter (`projects/barberia-app/`):**
- Feature `barber_schedule/` extendido con capas domain/data/presentation para agenda diaria
- `BarberSchedulePage` en `/barber/schedule` — reemplaza placeholder del router
- Consumo de `GET /barber/schedule?date=YYYY-MM-DD` vía `GetBarberScheduleUseCase`
- `ScheduleDateHeader` — navegación Hoy / Mañana / DatePicker / chevrons ±1 día
- `ScheduleAppointmentTile` — hora, cliente, servicio, `AppointmentStatusChip` (solo lectura)
- Estados UI: loading, error + reintentar, empty state, pull-to-refresh
- Orden cronológico confiado al API (sin reordenar en cliente)
- Tests: `barber_schedule_dtos_test.dart` (3) · `barber_schedule_page_test.dart` (5)

**Criterios SPEC cubiertos:**
- US-011: citas con hora, cliente, servicio y estado ✅ · orden cronológico ✅ · navegación entre días ✅

**Validación:** `flutter analyze` ✅ · `flutter test` (78) ✅

**Siguiente tarea:** T-062 — acciones de cambio de estado en tiles de agenda

### T-062 — Notas de implementación (2026-07-09)

**Estado:** Completada  
**Historia:** US-012 — Gestionar estado de citas

**Backend (`projects/barberia-api/`):**
- `PATCH /api/v1/barber/appointments/{id}/status` operativo (reemplaza stub 501)
- `UpdateBarberAppointmentStatusUseCase` + matriz `status_transitions.py` (ADR-2)
- `InvalidStatusTransitionError`, `AppointmentNotUpdatableError` — errores de dominio
- `AppointmentRepository.update_status()` — mutación atómica + fila en `appointment_status_history`
- `no_show` solo si `now >= scheduled_start` (ADR-3); 404 anti-enumeración si cita ajena
- Tests: `test_barber_appointment_status.py` (14 casos) · `test_role_guards.py` actualizado

**Flutter (`projects/barberia-app/`):**
- `allowedBarberActions` — helper de transiciones UI (paridad con backend)
- `UpdateBarberAppointmentStatusUseCase` + PATCH en datasource/repository
- `ScheduleAppointmentTile` — acciones contextuales, diálogos irreversibles, snackbar, invalidate
- Tests: `appointment_status_actions_test.dart` (8) · `barber_schedule_page_test.dart` extendido (8)

**Criterios SPEC cubiertos:**
- US-012: `pendiente → confirmada → en_progreso → completada` ✅ · `no_show` ✅ · solo citas propias ✅ · historial registrado ✅

**Validación:** `pytest` (173) ✅ · `flutter analyze` ✅ · `flutter test` (89) ✅

**Siguiente tarea:** T-063 — extender historial a cancelación cliente y void admin

### T-063 — Notas de implementación (2026-07-09)

**Estado:** Completada  
**Historia:** US-012 — Gestionar estado de citas (criterio: historial registrado)

**Backend (`projects/barberia-api/`):**
- `_append_status_history()` — punto único de escritura en `appointment_status_history` (ADR-T063-1)
- `AppointmentRepository.cancel()` — registra historial con `changed_by_user_id`; acepta `cancellation_reason` opcional (contrato T-064)
- `CancelAppointmentUseCase` — pasa `changed_by_user_id=client_user_id` al cancelar
- Sin historial en `create()` — creación no es transición de estado (ADR-T063-2)
- Tests: `test_cancel_records_status_history` (parametrizado pendiente/confirmada) · `test_chained_status_transitions_record_multiple_history_rows`

**Criterios SPEC cubiertos:**
- US-012: historial en transiciones barbero ✅ (T-062) · historial en cancelación cliente ✅ · contrato listo para void admin (T-064) ✅

**Validación:** `pytest` (176) ✅ · `flutter analyze` ✅ · `flutter test` (89) ✅

**Siguiente tarea:** T-064 — anulación de cita por admin con motivo

### T-064 — Notas de implementación (2026-07-09)

**Estado:** Completada  
**Historia:** US-019 — Anular cita (admin)

**Backend (`projects/barberia-api/`):**
- `PATCH /api/v1/admin/appointments/{id}/void` operativo bajo `require_admin`
- `VoidAppointmentUseCase` + `is_admin_voidable_status()` — estados `pendiente`, `confirmada`, `en_progreso`, `no_show`; motivo obligatorio (3–500 chars); sin ventana 2 h
- Reutiliza `AppointmentRepository.cancel()` — estado terminal `cancelada`, historial y slot libre
- `AuditLogRepository.log_appointment_voided()` — acción `appointment_voided` con motivo y `from_status`
- Schema `VoidAppointmentRequest` · respuesta `AppointmentResponse`
- Tests: `test_void_appointment.py` (19) · `test_role_guards.py::test_admin_void_requires_admin`

**Flutter (`projects/barberia-app/`):**
- `AdminClientAppointment.canBeVoidedByAdmin()` — paridad con política backend
- `VoidAdminAppointmentUseCase` + PATCH en datasource/repository
- `AdminClientAppointmentsDialog` — botón «Anular cita» con diálogo de motivo obligatorio
- Tests: `void_admin_appointment_test.dart` (6)

**Criterios SPEC cubiertos:**
- US-019: anular cualquier cita previa a `completada` ✅ · motivo obligatorio ✅ · slot libre y visibilidad cliente/barbero ✅

**Validación:** `pytest` (196) ✅ · `flutter analyze` ✅ · `flutter test` (95) ✅

**Siguiente tarea:** T-070 — tests unitarios del dominio de reservas y cancelación

---

## Fase 7 — Calidad y endurecimiento MVP

| ID | Tarea | Responsable | Estado |
|----|-------|-------------|--------|
| T-070 | Tests unitarios del dominio de reservas y cancelación | Developer | `[~]` |
| T-071 | Tests de integración backend para auth, disponibilidad y citas | Developer | `[ ]` |
| T-072 | Tests básicos de frontend para login, listado de servicios y reserva | Developer | `[ ]` |
| T-073 | Hardening de manejo de errores y estados vacíos en UI | Developer | `[ ]` |

---

## Fase 8 — Validación final

| ID | Tarea | Responsable | Estado |
|----|-------|-------------|--------|
| T-100 | Validación QA contra `docs/SPEC.md` | QA | `[x]` |
| T-101 | Revisar bugs encontrados y repriorizar | Product Manager / Architect | `[ ]` |
| T-102 | Code review técnico de MVP | Reviewer | `[ ]` |
| T-103 | Security audit básico | Security | `[ ]` |
| T-104 | Veredicto final de entrega | QA / Reviewer / Security | `[ ]` |

---

## Dependencias entre tareas

| Tarea | Depende de |
|------|------------|
| T-030 a T-035 | T-001 a T-008 |
| T-040 a T-045 | T-020 a T-023 |
| T-050 a T-056 | T-021 a T-025, T-040 a T-045 |
| T-060 a T-064 | T-050 a T-056 |
| T-070 a T-073 | Implementación de módulos previos |
| T-100+ | Todas las tareas MVP completadas |

---

## Corte recomendado de MVP

Para una primera entrega funcional, el orden recomendado es:

1. T-001 a T-008
2. T-020 a T-025
3. T-030 a T-035
4. T-040 a T-045
5. T-050 a T-056
6. T-060 a T-064
7. T-070 a T-104

---

## No entra en este plan inicial

- Historial de clientes para barbero (`US-013`)
- Estadísticas avanzadas (`US-018`)
- Notificaciones
- Pagos
- Multi-sucursal

---

## Bloqueos

| ID | Tarea | Motivo | Desde |
|----|-------|--------|-------|
| ~~B-001~~ | ~~T-104 (entrega MVP)~~ | ~~US-012 sin implementar (QA-001)~~ — **Resuelto en T-062/T-063** | 2026-07-09 |
| ~~B-002~~ | ~~T-104 (entrega MVP)~~ | ~~US-019 sin implementar (QA-002)~~ — **Resuelto en T-064** | 2026-07-09 |

Sin bloqueos funcionales activos. T-104 pendiente de T-102 (code review) y T-103 (security audit).

---

## Historial

| Fecha | Autor | Cambio |
|-------|-------|--------|
| 2026-07-08 | Architect | Plan técnico inicial del MVP y fases de implementación |
| 2026-07-09 | QA | Validación T-001..T-061 — veredicto CONDICIONAL; bloqueos B-001/B-002 por US-012 y US-019 |
| 2026-07-09 | QA | Re-validación T-062..T-064 — veredicto APROBADO; MVP funcional completo (17/17 historias) |
