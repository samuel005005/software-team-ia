# Software Factory Workflow

Metodología **Spec-Driven Development (SDD)** usando **Cursor** como plataforma de equipo de software asistido por IA.

## Principio

Cada rol SDD se define con:

1. **Cursor Rule** (`.cursor/rules/`) — comportamiento del rol
2. **Cursor Skill** (`.cursor/skills/`) — workflows reutilizables
3. **Prompt** (`prompts/`) — instrucción copiable en Agent Mode
4. **Documentos** (`docs/`) — artefactos del proceso

Cursor provee: LLM, contexto, edición, terminal y búsqueda.

### Modo manual vs orquestador

| Modo | Cómo | Cuándo |
|------|------|--------|
| **Manual** | Copiar prompt + activar rule en Agent Mode | Control fino, SPEC/ARCHITECTURE |
| **Automático** | `python -m factory next` o `pipeline` | Tareas repetitivas en `TASKS.md` |

El orquestador (`factory/`) usa **Cursor SDK**, lee `docs/TASKS.md`, compone prompts con rules/skills y ejecuta agentes. Ver [ORCHESTRATOR.md](ORCHESTRATOR.md).

### Flujo por requerimiento (cada tarea Developer)

```
SPEC (US + criterios)  →  ANALIZAR  →  CREAR  →  PROBAR  →  docs actualizados
```

El prompt del orquestador inyecta la historia de usuario desde `SPEC.md` y obliga al agente a validar criterios de aceptación antes de marcar `[x]`.

---

## Flujo oficial

```
Idea
  ↓
Product Manager          → docs/SPEC.md
  ↓
Architect                → docs/ARCHITECTURE.md + docs/TASKS.md
  ↓
Developer (por tarea)    → projects/<nombre>/ + CHANGELOG
  ↓
Tests
  ↓
QA                       → docs/QA_REPORT.md
  ↓
Reviewer                 → docs/REVIEW.md
  ↓
Security                 → docs/SECURITY_REPORT.md
  ↓
Entrega
```

### SDD por tarea (Developer)

```
SPEC → Architecture Decision → Task → Implementation → Tests → Review
```

---

## Artefactos y responsables

| Documento | Creado por | Actualizado por |
|-----------|------------|-----------------|
| `docs/SPEC.md` | Product Manager | PM |
| `docs/ARCHITECTURE.md` | Architect | Architect |
| `docs/TASKS.md` | Architect | Developer, QA |
| `docs/CHANGELOG.md` | Todos | Quien haga cambios |
| `docs/PROJECT_ANALYSIS.md` | Skill `project_analysis` | — |
| `docs/QA_REPORT.md` | QA | QA |
| `docs/REVIEW.md` | Reviewer | Reviewer |
| `docs/SECURITY_REPORT.md` | Security | Security |

Plantillas en `docs/templates/`.

---

## Roles (Cursor Rules)

| Rule | Rol | Salida principal |
|------|-----|------------------|
| `product_manager` | Especificación | `SPEC.md` |
| `architect` | Diseño técnico | `ARCHITECTURE.md`, `TASKS.md` |
| `developer` | Implementación | `projects/` |
| `qa` | Validación funcional | `QA_REPORT.md` |
| `reviewer` | Code review | `REVIEW.md` |
| `security` | Auditoría | `SECURITY_REPORT.md` |

Activar en Cursor: `@product_manager`, `@architect`, etc., o "Actúa como [rol]".

---

## Skills (workflows reutilizables)

| Skill | Uso |
|-------|-----|
| `project_analysis` | Analizar proyecto existente |
| `feature_design` | Diseñar feature y crear tareas |
| `flutter_feature` | Implementar feature Flutter (Clean Architecture) |
| `backend_feature` | Implementar feature backend |
| `database_change` | Migraciones y esquema |
| `bug_fix` | Corregir bugs con regresión |
| `refactor` | Mejorar código sin cambiar comportamiento |
| `testing` | Crear suite de pruebas |
| `code_review` | Revisión estructurada |
| `security_audit` | Auditoría de seguridad |

Ubicación: `.cursor/skills/<nombre>/SKILL.md`

---

## Fase 1 — Análisis (Product Manager)

**Prompt:** `prompts/new_project.md` o `prompts/analyze_existing_project.md`  
**Skill opcional:** `project_analysis` (proyectos existentes)

**Checklist:**
- [ ] Visión y objetivos
- [ ] Usuarios y roles
- [ ] Historias con criterios de aceptación
- [ ] Reglas de negocio
- [ ] MVP delimitado
- [ ] Aprobación humana del SPEC

---

## Fase 2 — Arquitectura (Architect)

**Entrada:** `docs/SPEC.md`  
**Salida:** `docs/ARCHITECTURE.md`, `docs/TASKS.md`

**Principios:** Clean Architecture, SOLID, patrones cuando aporten valor.

**Checklist:**
- [ ] Stack justificado
- [ ] Estructura de carpetas
- [ ] Modelo de datos / módulos
- [ ] Tareas pequeñas con IDs y dependencias
- [ ] Seguridad by design

---

## Fase 3 — Implementación (Developer)

**Entrada:** SPEC + ARCHITECTURE + TASKS (una tarea por sesión)  
**Prompt:** `prompts/implement_feature.md`  
**Skills:** `flutter_feature`, `backend_feature`, `database_change`, según tarea

**Checklist por tarea:**
- [ ] Requisito SPEC identificado antes de codificar
- [ ] Una sola tarea implementada
- [ ] Clean Architecture respetada
- [ ] Tests donde aplique
- [ ] `TASKS.md` y `CHANGELOG.md` actualizados
- [ ] Lint y tests pasan

---

## Fase 4 — QA

**Entrada:** SPEC + implementación  
**Salida:** `docs/QA_REPORT.md`  
**Skill:** `testing`

**Checklist:**
- [ ] Criterios de aceptación validados
- [ ] Reglas de negocio verificadas
- [ ] Bugs documentados con severidad
- [ ] Veredicto emitido

---

## Fase 5 — Code Review

**Entrada:** código + QA_REPORT  
**Salida:** `docs/REVIEW.md`  
**Skill:** `code_review`

---

## Fase 6 — Security

**Entrada:** código + ARCHITECTURE  
**Salida:** `docs/SECURITY_REPORT.md`  
**Prompt:** `prompts/security_audit.md`  
**Skill:** `security_audit`

---

## Flujo: Proyecto nuevo

1. Copiar plantillas de `docs/templates/` → `docs/` (renombrar proyecto).
2. **PM** + `prompts/new_project.md` → `SPEC.md`.
3. Aprobar SPEC con usuario humano.
4. **Architect** → `ARCHITECTURE.md` + `TASKS.md`.
5. **Developer** por cada `T-XXX` + skill correspondiente.
6. **QA** → `QA_REPORT.md`.
7. **Reviewer** → `REVIEW.md`.
8. **Security** → `SECURITY_REPORT.md`.
9. Veredicto final de entrega.

## Flujo: Proyecto existente

1. Skill `project_analysis` → `PROJECT_ANALYSIS.md`.
2. **PM** + `prompts/analyze_existing_project.md` → actualizar `SPEC.md`.
3. **Architect** → documentar arquitectura real.
4. Continuar desde Fase 3.

---

## Principios de ingeniería

- **SDD:** SPEC es fuente de verdad funcional; ARCHITECTURE la técnica.
- **Clean Architecture:** dominio independiente de frameworks.
- **SOLID** y patrones solo cuando resuelven problemas reales.
- **Incremental:** una tarea pequeña por sesión de Developer.
- **Documentación:** si no está en `docs/`, no existe para el equipo.

---

## Recuperar framework Python anterior

```bash
git log --oneline | grep backup
git show 63891e5 --stat
```

Ver `docs/CLEANUP_REPORT.md`.
