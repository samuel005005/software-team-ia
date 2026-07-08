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
| T-032 | Implementar pantalla de login/registro Flutter | US-001, US-002 | Developer | `[ ]` |
| T-033 | Implementar perfil cliente editable | US-008 | Developer | `[ ]` |
| T-034 | Implementar perfil profesional del barbero | US-009 | Developer | `[ ]` |
| T-035 | Implementar guards de acceso por rol | US-002 | Developer | `[ ]` |

---

## Fase 4 — Catálogo y configuración operativa

| ID | Tarea | Historia | Responsable | Estado |
|----|-------|----------|-------------|--------|
| T-040 | Implementar API y pantallas para listar servicios activos | US-003 | Developer | `[ ]` |
| T-041 | Implementar CRUD admin de servicios | US-015 | Developer | `[ ]` |
| T-042 | Implementar CRUD admin de barberos | US-014 | Developer | `[ ]` |
| T-043 | Implementar asignación de servicios por barbero | US-014, regla de negocio servicios por barbero | Developer | `[ ]` |
| T-044 | Implementar gestión de clientes desde admin | US-017 | Developer | `[ ]` |
| T-045 | Implementar configuración del horario del local | US-016 | Developer | `[ ]` |

---

## Fase 5 — Disponibilidad y reservas

| ID | Tarea | Historia | Responsable | Estado |
|----|-------|----------|-------------|--------|
| T-050 | Implementar disponibilidad recurrente del barbero | US-010 | Developer | `[ ]` |
| T-051 | Implementar consulta de barberos disponibles por servicio y fecha | US-004 | Developer | `[ ]` |
| T-052 | Implementar algoritmo de generación de slots reservables | US-004, US-005 | Developer | `[ ]` |
| T-053 | Implementar creación transaccional de citas con confirmación automática | US-005 | Developer | `[ ]` |
| T-054 | Implementar pantalla Flutter de reserva de cita | US-004, US-005 | Developer | `[ ]` |
| T-055 | Implementar historial de citas del cliente | US-007 | Developer | `[ ]` |
| T-056 | Implementar cancelación con regla de 2 horas | US-006 | Developer | `[ ]` |

---

## Fase 6 — Agenda del barbero y operación diaria

| ID | Tarea | Historia | Responsable | Estado |
|----|-------|----------|-------------|--------|
| T-060 | Implementar endpoint de agenda diaria/semanal del barbero | US-011 | Developer | `[ ]` |
| T-061 | Implementar pantalla Flutter de agenda del barbero | US-011 | Developer | `[ ]` |
| T-062 | Implementar cambios de estado de cita (`confirmada`, `en_progreso`, `completada`, `no_show`) | US-012 | Developer | `[ ]` |
| T-063 | Registrar historial de cambios de estado | US-012 | Developer | `[ ]` |
| T-064 | Implementar anulación de cita por admin con motivo | US-019 | Developer | `[ ]` |

---

## Fase 7 — Calidad y endurecimiento MVP

| ID | Tarea | Responsable | Estado |
|----|-------|-------------|--------|
| T-070 | Tests unitarios del dominio de reservas y cancelación | Developer | `[ ]` |
| T-071 | Tests de integración backend para auth, disponibilidad y citas | Developer | `[ ]` |
| T-072 | Tests básicos de frontend para login, listado de servicios y reserva | Developer | `[ ]` |
| T-073 | Hardening de manejo de errores y estados vacíos en UI | Developer | `[ ]` |

---

## Fase 8 — Validación final

| ID | Tarea | Responsable | Estado |
|----|-------|-------------|--------|
| T-100 | Validación QA contra `docs/SPEC.md` | QA | `[ ]` |
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
| — | — | Sin bloqueos activos | — |

---

## Historial

| Fecha | Autor | Cambio |
|-------|-------|--------|
| 2026-07-08 | Architect | Plan técnico inicial del MVP y fases de implementación |
