# Changelog — Barbería App

> Registro de cambios por fase del workflow de la Software Factory.

Formato basado en [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- 

### Changed
- 

### Fixed
- 

### Security
- 

---

## [2026-07-08] — Fase: Developer — T-031 (Login + refresh JWT)

### Added
- `POST /api/v1/auth/login` y `POST /api/v1/auth/refresh`
- `LoginUseCase`, `RefreshSessionUseCase`, `JwtService`
- Tabla `refresh_tokens` + migración `0004_refresh_tokens`
- Rotación de refresh token en cada renovación
- Tests: `test_login.py` (8 casos)

### Security
- Refresh tokens almacenados como SHA-256 (nunca en claro en DB)
- Access JWT firmado HS256 con expiración configurable

---

### Added
- `POST /api/v1/auth/register` — registro cliente con `201 Created`
- `RegisterClientUseCase` + `UserRepository`
- Hash de contraseña con `bcrypt`
- `RegisterResponse` (id, email, full_name, message)
- Tests: `test_register_client.py` (7 casos) + `conftest.py`

### Changed
- `requirements.txt` — `bcrypt` en lugar de `passlib`

### Security
- Contraseñas hasheadas con bcrypt antes de persistir

---

### Added
- Modelos SQLAlchemy en `app/infrastructure/db/models/`
- Migración `0002_domain_tables` — 10 tablas de dominio MVP
- Migración `0003_appointment_constraints` — anti doble reserva + rango válido
- `calculate_scheduled_end()` en dominio
- Tests: `test_models_metadata`, `test_appointments_constraints`

### Changed
- `alembic/env.py` importa modelos para autogenerate
- `docs/TASKS.md` — Fase 2 completada

### Security
- Passwords solo como `password_hash` en tabla `users` (sin lógica auth aún)

---

### Added
- Proyecto `projects/barberia-api/` — FastAPI modular
- Routers stub MVP: auth, users, barbers, services, availability, appointments, admin
- SQLAlchemy + Alembic + migración inicial `0001_initial`
- `docker-compose.yml` para PostgreSQL 15
- Enums de dominio: `UserRole`, `AppointmentStatus`, `Weekday`
- Schemas Pydantic base y contrato `Repository`
- Tests backend: health, stubs 501, enums (8 tests)

### Changed
- `.gitignore` — incluye `projects/barberia-api/`
- `docs/ARCHITECTURE.md` — ruta real del backend

---

## [2026-07-08] — Fase: Developer — T-005 (Secure storage)

### Added
- `flutter_secure_storage` para tokens JWT y rol
- `SessionPersistence` — guardar/restaurar/limpiar sesión
- `sessionBootstrapProvider` — restauración al iniciar app
- `InMemorySecureStorageService` para tests
- Tests: `session_persistence_test`, `session_bootstrap_provider_test`

### Changed
- `SessionNotifier.signInAs` / `signOut` persisten en secure storage
- `BarberiaApp` muestra loading durante bootstrap de sesión
- `docs/ARCHITECTURE.md` sincronizado con estructura real (T-001..T-005)

### Security
- Tokens JWT ya no viven solo en memoria; se almacenan en secure storage

---

## [2026-07-08] — Fase: Developer — T-004 (HTTP + Auth interceptors)

### Added
- Contrato `AuthTokenProvider` y `AuthTokenStore` en memoria
- `ApiClientFactory` con interceptores: auth, unauthorized (401), error mapping, logging
- `RemoteDataSource` base con `execute()` retornando `Result<T>`
- `NetworkConstants` con rutas públicas de auth
- Tests: `auth_interceptor_test`, `unauthorized_interceptor_test`, `remote_data_source_test`, `auth_token_store_test`

### Changed
- `apiClientProvider` movido a `network_providers.dart` con wiring de sesión
- Login mock y logout limpian tokens JWT además de sesión de navegación
- `core/providers` separado en `app_config_provider` y `network_providers`

---

## [2026-07-08] — Fase: Developer — T-003 (Estado global)

### Added
- Estado global base `AppState` con `themeMode`, `locale`, `isInitialized`, `isGlobalLoading`
- `AppStateNotifier` y providers derivados (`themeModeProvider`, `appLocaleProvider`, `appInitializedProvider`, `globalLoadingProvider`)
- Tests de providers: `app_state_providers_test` (3 casos)
- Soporte de tema oscuro en `AppTheme.dark`

### Changed
- `BarberiaApp` ahora consume estado global para `themeMode` y `locale`
- Login temporal integrado con `globalLoading` y toggle de tema para validar providers
- `docs/TASKS.md` y `docs/QA_REPORT.md` actualizados

---

## [2026-07-08] — Fase: Developer — T-002 (Navegación)

### Added
- Navegación GoRouter con rutas públicas (`/login`, `/register`) y protegidas por rol
- `RouterRedirect` — guards de autenticación y autorización por rol (cliente/barbero/admin)
- `SessionNotifier` en memoria + `RouterRefreshNotifier` para router reactivo
- `AuthenticatedShell` con bottom navigation adaptada por rol
- Rutas admin: `/admin/dashboard`, `/admin/services`, `/admin/barbers`, `/admin/users`, `/admin/business-hours`
- Login temporal por rol (solo navegación, sin API)
- Tests: `router_redirect_test` (6 casos), widgets de login/navegación/logout

### Changed
- `appRouterProvider` recibe `Ref` para redirect reactivo
- Eliminada `BootstrapPage`; raíz `/` redirige según sesión
- `docs/TASKS.md` y `docs/QA_REPORT.md` actualizados

### Removed
- Pantalla bootstrap T-001 (reemplazada por flujo login → shell)

---

## [2026-07-08] — Fase: Developer — T-001 (Clean Architecture)

### Added
- Capa `application/` en features con contrato base `UseCase<T, Params>`
- `Result<T>` funcional (`Success` / `Error`) y tipos `Failure` de dominio
- Mappers: `ExceptionMapper`, `DioExceptionMapper`, mixin `DioSafeCaller`
- Pantalla `BootstrapPage` (sin lógica de negocio)
- Estructura completa por feature: `domain/`, `data/`, `application/`, `presentation/`
- Tests: `exception_mapper_test`, `dio_exception_mapper_test`, `use_case_test`, widget bootstrap

### Changed
- GoRouter reducido a ruta bootstrap `/`; rutas de negocio como constantes para T-002
- Eliminadas pantallas placeholder de auth, citas, servicios y reservas
- `feature_scaffold` reemplazado por `AppScaffold` genérico en `shared/`
- `docs/TASKS.md` con notas de implementación T-001
- `docs/QA_REPORT.md` con validación técnica de T-001

### Fixed
- Test de arranque (texto duplicado en login placeholder anterior)
- Exhaustividad de `DioExceptionType.transformTimeout` en mapper

---

## [2026-07-08] — Infraestructura Software Factory (Cursor)

### Added
- **10 Skills** en `.cursor/skills/`: `project_analysis`, `feature_design`, `flutter_feature`, `backend_feature`, `database_change`, `bug_fix`, `refactor`, `testing`, `code_review`, `security_audit`
- **Plantillas** en `docs/templates/` (SPEC, ARCHITECTURE, TASKS, QA_REPORT, SECURITY_REPORT, REVIEW, PROJECT_ANALYSIS, CHANGELOG)
- `docs/QA_REPORT.md` y `docs/SECURITY_REPORT.md` como artefactos separados de revisión
- Workflow SDD documentado con skills y reportes independientes

### Changed
- Rules en `.cursor/rules/` ampliadas con SDD, Clean Architecture, SOLID y formatos de entrega profesionales
- `docs/SOFTWARE_FACTORY_WORKFLOW.md` actualizado con flujo PM → Security y skills
- `README.md` y `README_AI_WORKFLOW.md` alineados con nueva estructura
- QA y Security ahora generan reportes dedicados (`QA_REPORT.md`, `SECURITY_REPORT.md`) en lugar de solo secciones en REVIEW

---

## [2026-07-08] — Fase: Developer — T-001

### Added
- Reestructura profesional de `projects/barberia-app/lib/` con capas `app/`, `core/`, `shared/` y `features/`
- Módulos feature iniciales: `auth`, `appointments`, `services`, `client_booking`, `barber_schedule`, `profile`
- Configuración base de **Riverpod** (`ProviderScope`, providers de app y core)
- Configuración base de **GoRouter** con rutas placeholder alineadas a `docs/ARCHITECTURE.md`
- Configuración base de **Dio** (`ApiClient`) con timeouts y logging en desarrollo
- Manejo inicial de ambientes (`dev`, `staging`, `production`) vía `APP_ENV`
- Pantallas placeholder por módulo sin lógica de negocio
- Test de arranque (`test/widget_test.dart`) y `analysis_options.yaml`

### Changed
- `pubspec.yaml` actualizado con dependencias `flutter_riverpod`, `go_router` y `dio`
- `main.dart` migrado de Hello World a bootstrap de `BarberiaApp`
- `README.md` del proyecto Flutter actualizado con estructura y comandos
- Tarea **T-001** marcada como completada en `docs/TASKS.md`

---

## [2026-07-08] — Fase: Product Manager

### Added
- Especificación inicial del producto en `docs/SPEC.md`
- 19 historias de usuario (17 MVP, 2 Fase 2)
- Reglas de negocio (RN-01 a RN-12)
- Definición de roles: Cliente, Barbero, Administrador
- Alcance MVP y fuera de alcance documentados

---

## [2026-07-08] — Fase: Architect

### Added
- Arquitectura inicial del sistema en `docs/ARCHITECTURE.md`
- Modelo de datos inicial para usuarios, servicios, disponibilidad y citas
- Definición de arquitectura frontend Flutter y backend REST
- Plan técnico de implementación por fases en `docs/TASKS.md`

### Changed
- Decisión de reutilizar `projects/barberia-app/` solo como bootstrap Flutter y migrar su estructura interna

---

## Plantilla de entrada por fase

```markdown
## [YYYY-MM-DD] — Fase: [PM / Architect / Developer / QA / Reviewer / Security]

### Added
- Descripción del cambio

### Changed
- 

### Fixed
- 
```

## Historial

| Fecha | Fase | Resumen |
|-------|------|---------|
| 2026-07-08 | Product Manager | SPEC inicial Barbería App |
| 2026-07-08 | Architect | Arquitectura y plan técnico inicial del MVP |
| 2026-07-08 | Infraestructura | Software Factory Cursor: Skills, templates, rules SDD |
