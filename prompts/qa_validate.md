# Prompt: Validación QA

Usar con la rule **qa** y la skill `testing`.

---

## Contexto

Validación formal contra `docs/SPEC.md` del alcance indicado abajo.

## Referencias obligatorias

- `docs/SPEC.md` — historias y criterios de aceptación
- `docs/ARCHITECTURE.md` — stack y comandos de test
- `docs/TASKS.md` — tareas del alcance (deben estar `[x]`)
- `docs/CHANGELOG.md`
- Código y tests en `projects/`

## Tu tarea

Actúa como **QA Agent**.

1. **Alcance** — valida solo lo indicado en la sección «Alcance de esta validación» del prompt del orquestador.
2. **Criterios** — cada criterio de aceptación de las US del alcance debe tener evidencia (test ejecutado o verificación manual documentada).
3. **Reglas de negocio** — valida RN-XX del SPEC que apliquen al alcance.
4. **Tests** — ejecuta los comandos del stack (pytest, flutter test, npm test, etc.) y registra resultado PASS/FAIL.
5. **Bugs** — si encuentras fallos, documéntalos como BUG-XXX con severidad y pasos para reproducir.
6. **Bloqueos** — si un bug CRITICAL impide entregar, marca tareas afectadas como `[!]` en TASKS.md.
7. **Reporte** — actualiza `docs/QA_REPORT.md` con el formato de la rule QA.

## Formato del veredicto (obligatorio)

Al final de `docs/QA_REPORT.md`, sección `## Veredicto`, usa **exactamente** uno de:

- **APROBADO** — todo el alcance cumple SPEC y tests pasan
- **CONDICIONAL** — entregable con observaciones menores documentadas
- **RECHAZADO** — fallos CRITICAL/MAJOR o criterios sin cumplir

## Qué NO hacer

- No modifiques código de producción (solo tests si es imprescindible y está autorizado).
- No cambies SPEC ni ARCHITECTURE.
- No apruebes sin ejecutar tests del stack.

## Salida final

Resume: veredicto, US validadas, comandos ejecutados, bugs abiertos por severidad.
