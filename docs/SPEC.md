# Especificación — Barbería App

> Documento vivo. Actualizado por el **Product Manager Agent** en Cursor.  
> Versión: 1.0 — 2026-07-08

---

# Información del producto

## Nombre del proyecto

**Barbería App** (`barberia-app`)

## Descripción

Plataforma digital para la gestión integral de citas en una barbería. Permite a los clientes reservar servicios en línea, a los barberos administrar su agenda y disponibilidad, y al administrador del negocio controlar usuarios, servicios, horarios y métricas operativas básicas.

## Problema que resuelve

Las barberías que gestionan citas de forma manual (llamadas, WhatsApp, agenda en papel) enfrentan:

- **Doble reserva** de horarios por falta de sincronización.
- **Pérdida de tiempo** del barbero y del cliente coordinando disponibilidad.
- **Falta de visibilidad** para el administrador sobre ocupación, cancelaciones y rendimiento.
- **Experiencia inconsistente** para el cliente (sin historial, sin confirmaciones claras).

## Objetivo principal

Ofrecer una plataforma centralizada donde clientes reserven citas de forma autónoma, barberos gestionen su agenda con claridad y el administrador supervise la operación del negocio con reglas de negocio consistentes y trazables.

---

# Usuarios del sistema

## Cliente

| Aspecto | Detalle |
|---------|---------|
| **Necesidades** | Reservar citas sin llamar, ver disponibilidad real, gestionar sus citas y consultar historial |
| **Acciones principales** | Registrarse, iniciar sesión, ver servicios y barberos, reservar/cancelar citas, ver historial |
| **Permisos** | CRUD sobre su propio perfil; crear y cancelar sus propias citas; leer servicios y disponibilidad pública |

## Barbero

| Aspecto | Detalle |
|---------|---------|
| **Necesidades** | Conocer su agenda del día, definir cuándo está disponible, gestionar citas asignadas |
| **Acciones principales** | Configurar disponibilidad, ver agenda diaria/semanal, aceptar o gestionar citas, consultar historial de clientes atendidos |
| **Permisos** | Editar su perfil profesional; gestionar su disponibilidad; ver y actualizar estado de citas asignadas a él; leer historial de clientes que ha atendido |

## Administrador

| Aspecto | Detalle |
|---------|---------|
| **Necesidades** | Control total de la operación: personal, servicios, horarios del negocio y visión general |
| **Acciones principales** | Gestionar usuarios (clientes y barberos), servicios, horarios del local, consultar estadísticas básicas |
| **Permisos** | CRUD sobre usuarios, barberos y servicios; configurar horarios del negocio; acceso a reportes y estadísticas; anular citas en casos excepcionales |

---

# Funcionalidades principales

## Clientes

| # | Funcionalidad | Descripción |
|---|---------------|-------------|
| F-C01 | Registro e inicio de sesión | Crear cuenta con email/teléfono y autenticarse de forma segura |
| F-C02 | Perfil personal | Ver y editar nombre, contacto y preferencias básicas |
| F-C03 | Ver servicios disponibles | Listar servicios con nombre, duración y precio |
| F-C04 | Consultar barberos disponibles | Ver barberos activos y su disponibilidad para un servicio/fecha |
| F-C05 | Reservar citas | Seleccionar servicio, barbero, fecha y hora; confirmar reserva |
| F-C06 | Cancelar citas | Cancelar citas propias respetando política de cancelación |
| F-C07 | Ver historial de citas | Consultar citas pasadas y futuras con estado |

## Barberos

| # | Funcionalidad | Descripción |
|---|---------------|-------------|
| F-B01 | Perfil profesional | Nombre, foto, especialidades y bio breve |
| F-B02 | Definir disponibilidad | Bloques de horario disponible por día de la semana |
| F-B03 | Ver agenda diaria | Vista del día con citas programadas |
| F-B04 | Aceptar o gestionar citas | Confirmar, marcar en progreso, completar o reportar no-show |
| F-B05 | Consultar historial de clientes | Ver citas previas con un cliente (limitado a sus atenciones) |

## Administrador

| # | Funcionalidad | Descripción |
|---|---------------|-------------|
| F-A01 | Gestionar usuarios | Alta, baja y edición de clientes |
| F-A02 | Gestionar barberos | Alta, baja y edición de barberos; asignar servicios que realizan |
| F-A03 | Gestionar servicios | CRUD de servicios (nombre, duración, precio, activo/inactivo) |
| F-A04 | Configurar horarios | Horario de apertura/cierre del local y días no laborables |
| F-A05 | Consultar estadísticas básicas | Citas por día/semana, cancelaciones, ocupación por barbero |

---

# Reglas de negocio

| ID | Regla |
|----|-------|
| RN-01 | Un horario ocupado **no puede reservarse dos veces** para el mismo barbero. |
| RN-02 | Toda cita debe pertenecer a **exactamente un cliente y un barbero**. |
| RN-03 | Toda cita debe estar asociada a **un servicio** con duración definida. |
| RN-04 | Las citas tienen **estados**: `pendiente`, `confirmada`, `en_progreso`, `completada`, `cancelada`, `no_show`. |
| RN-05 | Solo se pueden reservar horarios **dentro de la disponibilidad del barbero** y del horario del local. |
| RN-06 | La duración de la cita se calcula según el **tiempo del servicio** seleccionado; no puede solaparse con otra cita del mismo barbero. |
| RN-07 | Un cliente solo puede **cancelar sus propias citas**. |
| RN-08 | Cancelación permitida hasta **X horas antes** del inicio (valor por confirmar; propuesta: 2 horas). |
| RN-09 | Citas en estado `completada` o `cancelada` **no son modificables** por el cliente. |
| RN-10 | Un barbero inactivo **no aparece** en disponibilidad para nuevas reservas. |
| RN-11 | Un servicio inactivo **no es reservable**. |
| RN-12 | El administrador puede anular cualquier cita con registro de motivo. |

---

# Historias de usuario

## Cliente

### US-001 — Registro de cuenta

**Como** cliente, **quiero** registrarme con email y contraseña, **para** acceder a la plataforma y reservar citas.

**Criterios de aceptación:**
- [ ] Puedo crear cuenta con email único y contraseña segura (mín. 8 caracteres).
- [ ] Recibo confirmación visual de registro exitoso.
- [ ] No puedo registrar un email ya existente.
- [ ] Tras registrarme, puedo iniciar sesión.

**Prioridad:** MVP

---

### US-002 — Inicio de sesión

**Como** cliente, **quiero** iniciar sesión con mis credenciales, **para** acceder a mis citas y reservar nuevas.

**Criterios de aceptación:**
- [ ] Puedo iniciar sesión con email y contraseña válidos.
- [ ] Recibo mensaje claro si las credenciales son incorrectas.
- [ ] Tras login exitoso, accedo a la vista principal del cliente.

**Prioridad:** MVP

---

### US-003 — Ver servicios disponibles

**Como** cliente, **quiero** ver la lista de servicios con duración y precio, **para** elegir qué reservar.

**Criterios de aceptación:**
- [ ] Veo nombre, duración (minutos) y precio de cada servicio activo.
- [ ] No veo servicios marcados como inactivos.
- [ ] La lista se muestra ordenada alfabéticamente o por categoría.

**Prioridad:** MVP

---

### US-004 — Consultar barberos y disponibilidad

**Como** cliente, **quiero** ver qué barberos están disponibles para un servicio y fecha, **para** elegir a quién reservar.

**Criterios de aceptación:**
- [ ] Al seleccionar servicio y fecha, veo barberos que ofrecen ese servicio.
- [ ] Veo slots de horario disponibles (no ocupados).
- [ ] No aparecen barberos inactivos.

**Prioridad:** MVP

---

### US-005 — Reservar cita

**Como** cliente, **quiero** reservar una cita seleccionando servicio, barbero, fecha y hora, **para** asegurar mi turno sin llamar.

**Criterios de aceptación:**
- [ ] Puedo completar el flujo: servicio → barbero → fecha/hora → confirmar.
- [ ] El sistema valida que el slot no esté ocupado (RN-01).
- [ ] La cita queda en estado `pendiente` o `confirmada` según política.
- [ ] Recibo confirmación con resumen (servicio, barbero, fecha, hora).
- [ ] No puedo reservar en el pasado.

**Prioridad:** MVP

---

### US-006 — Cancelar cita

**Como** cliente, **quiero** cancelar una cita futura, **para** liberar el horario si no puedo asistir.

**Criterios de aceptación:**
- [ ] Puedo cancelar solo mis propias citas en estado `pendiente` o `confirmada`.
- [ ] No puedo cancelar si faltan menos de X horas (RN-08).
- [ ] La cita pasa a estado `cancelada` y el slot queda libre.
- [ ] Recibo confirmación de cancelación.

**Prioridad:** MVP

---

### US-007 — Ver historial de citas

**Como** cliente, **quiero** ver mis citas pasadas y futuras, **para** llevar control de mis visitas.

**Criterios de aceptación:**
- [ ] Veo listado con fecha, servicio, barbero y estado.
- [ ] Puedo distinguir citas futuras de pasadas.
- [ ] Las citas se ordenan por fecha (próximas primero).

**Prioridad:** MVP

---

### US-008 — Editar perfil personal

**Como** cliente, **quiero** actualizar mi nombre y teléfono, **para** mantener mis datos de contacto al día.

**Criterios de aceptación:**
- [ ] Puedo editar nombre y teléfono.
- [ ] Los cambios se guardan y reflejan en mi perfil.
- [ ] No puedo cambiar mi email en MVP (o requiere verificación — ver preguntas pendientes).

**Prioridad:** MVP

---

## Barbero

### US-009 — Perfil profesional

**Como** barbero, **quiero** mantener mi perfil con nombre, foto y especialidades, **para** que los clientes me conozcan al reservar.

**Criterios de aceptación:**
- [ ] Puedo editar nombre para mostrar, foto y descripción breve.
- [ ] Mi perfil es visible para clientes al elegir barbero.
- [ ] Solo yo (o el admin) puedo editar mi perfil.

**Prioridad:** MVP

---

### US-010 — Definir disponibilidad

**Como** barbero, **quiero** configurar mis horarios disponibles por día, **para** que solo se reserven citas cuando puedo atender.

**Criterios de aceptación:**
- [ ] Puedo definir bloques de disponibilidad por día de la semana.
- [ ] Los slots fuera de mi disponibilidad no son reservables.
- [ ] Puedo actualizar disponibilidad futura sin afectar citas ya confirmadas.

**Prioridad:** MVP

---

### US-011 — Ver agenda diaria

**Como** barbero, **quiero** ver mi agenda del día, **para** organizar mi jornada de trabajo.

**Criterios de aceptación:**
- [ ] Veo citas del día con hora, cliente, servicio y estado.
- [ ] Las citas se muestran en orden cronológico.
- [ ] Puedo navegar entre días (hoy / mañana / fecha específica).

**Prioridad:** MVP

---

### US-012 — Gestionar estado de citas

**Como** barbero, **quiero** cambiar el estado de mis citas (confirmar, en progreso, completada, no-show), **para** reflejar el avance real del servicio.

**Criterios de aceptación:**
- [ ] Puedo pasar de `pendiente` → `confirmada` → `en_progreso` → `completada`.
- [ ] Puedo marcar `no_show` si el cliente no asiste.
- [ ] Solo gestiono citas asignadas a mí.
- [ ] Los cambios de estado quedan registrados.

**Prioridad:** MVP

---

### US-013 — Consultar historial de clientes

**Como** barbero, **quiero** ver el historial de citas de un cliente que he atendido, **para** ofrecer un servicio más personalizado.

**Criterios de aceptación:**
- [ ] Puedo ver citas previas con un cliente (solo las mías).
- [ ] Veo servicio, fecha y notas si existen.
- [ ] No accedo a datos de clientes que no he atendido.

**Prioridad:** Fase 2 (post-MVP)

---

## Administrador

### US-014 — Gestionar barberos

**Como** administrador, **quiero** dar de alta, editar y desactivar barberos, **para** mantener el equipo actualizado en la plataforma.

**Criterios de aceptación:**
- [ ] Puedo crear barbero con datos básicos y credenciales.
- [ ] Puedo editar datos y desactivar barbero (no eliminar si tiene historial).
- [ ] Barbero inactivo no aparece para nuevas reservas.

**Prioridad:** MVP

---

### US-015 — Gestionar servicios

**Como** administrador, **quiero** crear y editar servicios con duración y precio, **para** definir la oferta de la barbería.

**Criterios de aceptación:**
- [ ] Puedo crear servicio con nombre, duración (min) y precio.
- [ ] Puedo activar/desactivar servicios.
- [ ] Servicio inactivo no es reservable.

**Prioridad:** MVP

---

### US-016 — Configurar horarios del local

**Como** administrador, **quiero** definir horario de apertura y días cerrados, **para** que las reservas respeten el horario del negocio.

**Criterios de aceptación:**
- [ ] Puedo configurar hora apertura/cierre por día.
- [ ] Puedo marcar días no laborables (festivos).
- [ ] No se pueden reservar citas fuera del horario del local.

**Prioridad:** MVP

---

### US-017 — Gestionar usuarios (clientes)

**Como** administrador, **quiero** ver y gestionar cuentas de clientes, **para** resolver incidencias y moderar el acceso.

**Criterios de aceptación:**
- [ ] Puedo listar clientes registrados.
- [ ] Puedo desactivar cuenta de cliente.
- [ ] Puedo ver citas asociadas a un cliente.

**Prioridad:** MVP

---

### US-018 — Consultar estadísticas básicas

**Como** administrador, **quiero** ver métricas de citas y ocupación, **para** tomar decisiones operativas.

**Criterios de aceptación:**
- [ ] Veo total de citas por período (día/semana/mes).
- [ ] Veo tasa de cancelaciones y no-shows.
- [ ] Veo ocupación por barbero (citas completadas vs disponibles).

**Prioridad:** Fase 2 (post-MVP)

---

### US-019 — Anular cita (admin)

**Como** administrador, **quiero** anular cualquier cita con motivo, **para** resolver conflictos o emergencias.

**Criterios de aceptación:**
- [ ] Puedo anular cita en cualquier estado previo a `completada`.
- [ ] Debo indicar motivo de anulación.
- [ ] El slot queda liberado y cliente/barbero ven el cambio.

**Prioridad:** MVP

---

# Alcance inicial (MVP)

## Incluido en MVP

| Área | Funcionalidades |
|------|-----------------|
| **Auth** | Registro e inicio de sesión (cliente); login barbero y admin |
| **Cliente** | Perfil, ver servicios, ver disponibilidad, reservar, cancelar, historial |
| **Barbero** | Perfil, disponibilidad, agenda diaria, gestión de estados de cita |
| **Admin** | CRUD servicios, CRUD barberos, gestión básica de clientes, horarios del local, anulación de citas |
| **Negocio** | Estados de cita, anti doble-reserva, duración por servicio, política de cancelación |
| **Plataforma** | Una barbería (single-tenant); app móvil o web responsive (decisión en arquitectura) |

**Historias MVP:** US-001 a US-012, US-014 a US-017, US-019 (17 historias).

## Criterio de éxito del MVP

Un cliente puede reservar una cita end-to-end, un barbero la ve en su agenda y la gestiona, y el administrador puede configurar servicios, barberos y horarios sin doble reserva.

---

# Fuera de alcance

Funcionalidades **no incluidas** en la primera versión:

| # | Funcionalidad | Fase sugerida |
|---|---------------|---------------|
| 1 | Pagos en línea / pasarela de pago | Fase 3 |
| 2 | Notificaciones push / SMS / email automáticos | Fase 2 |
| 3 | Sistema de valoraciones y reseñas | Fase 3 |
| 4 | Programa de fidelización / puntos | Fase 3 |
| 5 | Multi-sucursal / multi-tenant | Fase 4 |
| 6 | Chat cliente-barbero | Fase 3 |
| 7 | Integración con Google Calendar / Outlook | Fase 3 |
| 8 | Reportes avanzados y exportación | Fase 2 |
| 9 | Historial de clientes para barbero (US-013) | Fase 2 |
| 10 | Estadísticas avanzadas (US-018) | Fase 2 |
| 11 | Recuperación de contraseña por email | Fase 2 |
| 12 | Reserva como invitado (sin registro) | Fase 2 |
| 13 | Lista de espera / waitlist | Fase 3 |
| 14 | App nativa separada iOS/Android (si MVP es PWA/web) | Evaluar post-MVP |

---

# Supuestos

- Una sola barbería opera en la plataforma (single-tenant).
- Los barberos y el administrador reciben credenciales creadas por el admin (no auto-registro de barberos).
- Zona horaria única del negocio (sin multi-timezone en MVP).
- Idioma: español.
- Moneda: definir (propuesta: DOP o USD según mercado objetivo).

---

# Riesgos

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Doble reserva por condición de carrera | Alto | Transacciones atómicas / bloqueo de slot al confirmar (decisión técnica del Architect) |
| Barberos no actualizan disponibilidad | Medio | Onboarding claro; recordatorios manuales en MVP |
| Política de cancelación mal definida | Medio | Confirmar X horas con el negocio antes de implementar |
| Scope creep hacia pagos/notificaciones | Alto | Mantener fuera de alcance explícito; priorizar MVP |
| Sin notificaciones, clientes olvidan citas | Medio | Incluir en Fase 2; MVP muestra confirmación en app |

---

# Preguntas pendientes

Decisiones a confirmar **antes de arquitectura**:

- [ ] **Plataforma:** ¿App móvil nativa (Flutter), web responsive o ambas?
- [ ] **Backend:** ¿Existe preferencia de stack (Firebase, Supabase, API propia)?
- [ ] **Cancelación:** ¿Cuántas horas antes se permite cancelar sin penalización? (propuesta: 2 h)
- [ ] **Confirmación de cita:** ¿Automática al reservar o requiere confirmación del barbero?
- [ ] **Moneda y mercado:** ¿RD$ (República Dominicana) u otra?
- [ ] **Registro de barberos:** ¿Solo admin crea cuentas o pueden auto-registrarse?
- [ ] **Campos de perfil:** ¿Foto obligatoria para barberos?
- [ ] **Servicios:** ¿Un barbero puede ofrecer solo subset de servicios?
- [ ] **Horario:** ¿Intervalos de reserva fijos (ej. cada 30 min) o según duración del servicio?
- [ ] **Proyecto existente:** ¿Partir de `projects/barberia-app/` (Flutter hello world) o greenfield?

---

# Historial

| Fecha | Autor | Cambio |
|-------|-------|--------|
| 2026-07-08 | Product Manager | Creación inicial de especificación Barbería App |
