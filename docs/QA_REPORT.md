# QA Report — Barbería App — 2026-07-09

## Resumen ejecutivo

Re-validación QA del MVP contra `docs/SPEC.md`, ejecutada tras la entrega de **T-062** (gestión de estados barbero), **T-063** (historial unificado de transiciones) y **T-064** (anulación admin US-019).

**Alcance validado:** T-001 — T-064 (17 historias MVP completas).

**Resultado de suites:**
- Backend: **196/196** tests pasando
- Flutter: **95/95** tests pasando
- Flutter analyze: **3 info** (`prefer_const_constructors` en tests admin; no bloquean)
- Factory CLI: **4/4** tests pasando

**Veredicto global:** **APROBADO** — Las 17 historias MVP y las reglas de negocio RN-01 — RN-12 cumplen criterios de aceptación con evidencia automatizada. Los bloqueos QA-001 y QA-002 de la validación anterior están resueltos.

**Nota de entrega (T-104):** El cierre formal del MVP sigue pendiente de **code review (T-102)** y **security audit (T-103)** según workflow SDD; no son fallos funcionales detectados en esta ronda.

---

## Alcance validado

| Área | Tareas | Estado QA |
|------|--------|-----------|
| Setup técnico | T-001 — T-008 | ✅ Validado |
| Modelo de datos y constraints | T-020 — T-025 | ✅ Validado |
| Auth y perfiles | T-030 — T-035 | ✅ Validado |
| Catálogo y admin operativo | T-040 — T-045 | ✅ Validado |
| Disponibilidad y reservas cliente | T-050 — T-056 | ✅ Validado |
| Agenda barbero | T-060 — T-061 | ✅ Validado |
| Gestión estados barbero + historial | T-062 — T-063 | ✅ Validado |
| Anulación admin | T-064 | ✅ Validado |
| Hardening / validación final | T-070 — T-104 | ⏳ Pendiente (fuera de alcance funcional MVP) |

**Fuera de alcance MVP (correctamente excluido):** US-013, US-018.

---

## Historias validadas

| ID | Historia | Estado | Evidencia |
|----|----------|--------|-----------|
| US-001 | Registro de cuenta | ✅ Aprobada | `test_register_client.py`, `register_page.dart`, widget tests auth |
| US-002 | Inicio de sesión | ✅ Aprobada | `test_login.py`, guards `test_role_guards.py`, `router_redirect_test.dart` |
| US-003 | Ver servicios disponibles | ✅ Aprobada | `test_services.py`, `ServicesPage`, `service_dtos_test.dart` |
| US-004 | Consultar barberos y disponibilidad | ✅ Aprobada | `test_availability*.py`, `book_appointment_page_test.dart` |
| US-005 | Reservar cita | ✅ Aprobada | `test_create_appointment.py`, wizard 4 pasos Flutter |
| US-006 | Cancelar cita | ✅ Aprobada | `test_cancel_appointment.py`, `cancel_appointment_test.dart` |
| US-007 | Ver historial de citas | ✅ Aprobada | `test_list_my_appointments.py`, `appointments_page_test.dart` |
| US-008 | Editar perfil personal | ✅ Aprobada | `test_profile_me.py`, `ProfilePage` cliente |
| US-009 | Perfil profesional barbero | ✅ Aprobada | `test_profile_me.py` (barber), `BarberProfilePage` |
| US-010 | Definir disponibilidad | ✅ Aprobada | `test_barber_availability.py`, `BarberAvailabilityPage` |
| US-011 | Ver agenda diaria | ✅ Aprobada | `test_barber_schedule.py` (13 casos), `barber_schedule_page_test.dart` (8 casos) |
| US-012 | Gestionar estado de citas | ✅ Aprobada | `test_barber_appointment_status.py` (14 casos), `appointment_status_actions_test.dart` (8), `barber_schedule_page_test.dart` (acciones), `test_cancel_records_status_history` |
| US-014 | Gestionar barberos | ✅ Aprobada | `test_admin_barbers.py`, `AdminBarbersPage` |
| US-015 | Gestionar servicios | ✅ Aprobada | `test_admin_services.py`, `AdminServicesPage` |
| US-016 | Configurar horarios del local | ✅ Aprobada | `test_admin_business_hours.py`, `AdminBusinessHoursPage` |
| US-017 | Gestionar usuarios (clientes) | ✅ Aprobada | `test_admin_clients.py`, `AdminUsersPage`, `void_admin_appointment_test.dart` |
| US-019 | Anular cita (admin) | ✅ Aprobada | `test_void_appointment.py` (19 casos), `void_admin_appointment_test.dart` (6 casos) |

**Resumen:** 17 aprobadas · 0 rechazadas.

---

## Reglas de negocio validadas

| ID | Regla | Estado | Evidencia |
|----|-------|--------|-----------|
| RN-01 | Horario ocupado no se reserva dos veces | ✅ | `test_appointments_constraints.py`, `test_create_appointment.py` (409), EXCLUDE constraint |
| RN-02 | Cita = 1 cliente + 1 barbero | ✅ | Modelo + `test_create_appointment.py` |
| RN-03 | Cita asociada a servicio con duración | ✅ | `calculate_scheduled_end()`, tests creación |
| RN-04 | Estados de cita definidos | ✅ | `test_domain_enums.py`, chips UI, respuestas API |
| RN-05 | Reserva dentro disponibilidad barbero y local | ✅ | `test_availability*.py`, `ListAvailableBarbersUseCase` |
| RN-06 | Duración por servicio, sin solapamiento | ✅ | `test_availability_slots.py`, constraint overlap |
| RN-07 | Cliente solo cancela sus citas | ✅ | `test_cancel_appointment.py` |
| RN-08 | Cancelación hasta 2 h antes | ✅ | `test_cancel_appointment.py`, `cancel_appointment_test.dart` |
| RN-09 | Completada/cancelada no modificables por cliente | ✅ | Tests cancelación rechazan estados finales |
| RN-10 | Barbero inactivo no en disponibilidad | ✅ | `test_availability.py`, `GET /barbers` filtra bookables |
| RN-11 | Servicio inactivo no reservable | ✅ | `test_admin_services.py`, availability 404 |
| RN-12 | Admin anula cualquier cita con motivo | ✅ | `test_void_appointment.py` (motivo obligatorio, audit log, slot libre, visibilidad cliente/barbero) |

---

## Bugs encontrados

| ID | Severidad | Descripción | Pasos | Estado |
|----|-----------|-------------|-------|--------|
| ~~QA-001~~ | ~~Mayor~~ | ~~US-012 no implementada~~ | — | **Cerrado** — T-062/T-063 |
| ~~QA-002~~ | ~~Mayor~~ | ~~US-019 no implementada~~ | — | **Cerrado** — T-064 |
| ~~QA-003~~ | ~~Menor~~ | ~~Mensaje stub incorrecto en endpoint de estado~~ | — | **Cerrado** — endpoint operativo en `barber.py` |
| QA-004 | Menor | Pantallas placeholder en rutas secundarias | Cliente `/home` y admin `/admin/dashboard` muestran `FeaturePlaceholderPage` | Conocido — no bloquea criterios SPEC |
| QA-005 | Menor | Lints info en tests Flutter admin | `flutter analyze` reporta 3× `prefer_const_constructors` en `void_admin_appointment_test.dart` | Abierto — cosmético |

**Bugs críticos:** 0  
**Bugs mayores (bloquean MVP):** 0

---

## Casos límite probados

| Caso | Resultado | Evidencia |
|------|-----------|-----------|
| Transición barbero sin auth | 401 | `test_status_update_requires_auth` |
| Cliente/admin cambian estado barbero | 403 | `test_status_update_rejects_client/admin` |
| Barbero A no modifica cita de barbero B | 404 | `test_status_update_wrong_barber` |
| Cadena pendiente→confirmada→en_progreso→completada | ✅ | `test_pendiente_to_confirmada`, `test_confirmada_to_en_progreso`, `test_en_progreso_to_completada` |
| no_show solo tras hora inicio | 400 si futuro | `test_no_show_before_start_rejected`, `test_confirmada_to_no_show` |
| Transición inválida desde completada/cancelada | 400 | `test_invalid_transition_completada_to_en_progreso`, `test_invalid_transition_cancelada` |
| Historial en transición barbero | ✅ | `test_status_history_recorded`, `test_chained_status_transitions_record_multiple_history_rows` |
| Historial en cancelación cliente | ✅ | `test_cancel_records_status_history` (pendiente/confirmada) |
| Agenda refleja nuevo estado | ✅ | `test_schedule_reflects_new_status` |
| Admin void sin ventana 2 h | ✅ | `test_void_success_confirmada` (cita a +5 h) |
| Void rechaza completada/cancelada | 400 | `test_void_rejects_terminal_statuses` |
| Void motivo vacío/corto | 422 | `test_void_rejects_invalid_reason` |
| Void libera slot disponibilidad | ✅ | `test_void_frees_slot_for_availability` |
| Void visible en historial cliente | ✅ | `test_void_visible_to_client` |
| Void visible en agenda barbero | ✅ | `test_void_visible_to_barber` |
| Audit log en void admin | ✅ | `test_void_records_audit_log` |
| UI barbero: acciones contextuales | ✅ | `appointment_status_actions_test.dart`, `barber_schedule_page_test.dart` |
| UI admin: motivo obligatorio en diálogo | ✅ | `void_admin_appointment_test.dart` |
| Doble reserva mismo slot | 409 | `test_create_appointment.py` |
| Cancelación en ventana límite 2 h | ✅ | `test_cancel_appointment.py` |
| Registro email duplicado | 409 | `test_register_duplicate_email_returns_409` |

---

## Tests ejecutados

| Comando | Resultado |
|---------|-----------|
| `cd projects/barberia-api && python -m pytest -q` | **196 passed** (85.3s) |
| `cd projects/barberia-app && flutter analyze` | **3 info** (prefer_const_constructors; sin errors/warnings) |
| `cd projects/barberia-app && flutter test` | **95 passed** |
| `python -m pytest tests/factory/test_run_aliases.py -q` | **4 passed** |

---

## Regresiones

No se detectaron regresiones en suites existentes tras T-062/T-063/T-064.

Verificaciones de no-regresión:
- Flujos cliente (listado, reserva, cancelación) intactos
- Agenda barbero (T-060/T-061) sin cambios adversos
- Guards por rol actualizados (`test_role_guards.py` incluye void admin y status barbero)
- Disponibilidad y generación de slots sin cambios adversos

---

## Veredicto: APROBADO

| Criterio | Resultado |
|----------|-----------|
| 17 historias MVP (US-001 — US-012, US-014 — US-017, US-019) | **APROBADO** |
| Reglas de negocio RN-01 — RN-12 | **APROBADO** |
| Flujo end-to-end SPEC (cliente reserva → barbero gestiona → admin puede anular) | **APROBADO** (evidencia por tests de integración) |
| Regresiones en suites | **APROBADO** |
| Bloqueos QA-001 / QA-002 | **RESUELTOS** |

**Pendiente para T-104 (entrega formal):**
1. Code review técnico (T-102)
2. Security audit básico (T-103)
3. Hardening opcional T-070 — T-073 (cobertura adicional, estados vacíos)

---

## Recomendaciones

1. **T-102 / T-103:** Ejecutar code review y security audit antes del veredicto final T-104.
2. **QA-005:** Aplicar `const` en constructores de `void_admin_appointment_test.dart` para limpiar analyze.
3. **QA-004:** Sustituir placeholders `/home` y `/admin/dashboard` o redirigir a rutas funcionales antes de demo comercial.
4. **T-070:** Añadir tests unitarios puros de dominio para `status_transitions.py` y `cancellation.py` (hoy cubiertos vía integración).
5. **T-061 follow-up:** Añadir test widget de estado error/reintentar en `BarberSchedulePage` (cobertura parcial).
6. **Manual smoke (opcional):** Validar flujo E2E en dispositivo: reserva → agenda barbero → completar → ver historial cliente.

---

## Historial QA

| Fecha | Alcance | Veredicto |
|-------|---------|-----------|
| 2026-07-08 | T-001 — T-051 (parcial) | APROBADO condicional (slots pendientes T-052) |
| 2026-07-09 (AM) | T-001 — T-061 | CONDICIONAL (US-012, US-019 pendientes) |
| 2026-07-09 (PM) | T-001 — T-064 | **APROBADO** (MVP funcional completo) |
