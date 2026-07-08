# Guía: Usar Cursor como Software Factory

Operar la fábrica de software con roles de IA en Cursor, sin framework de código.

---

## Concepto

Cada rol del equipo es:

| Componente | Ubicación | Función |
|------------|-----------|---------|
| **Rule** | `.cursor/rules/` | Comportamiento persistente del rol |
| **Skill** | `.cursor/skills/` | Workflow especializado reutilizable |
| **Prompt** | `prompts/` | Instrucción de la tarea en Agent Mode |
| **Docs** | `docs/` | Artefactos SDD |

---

## Configuración inicial (una vez)

1. Abre este repositorio en Cursor.
2. Verifica `.cursor/rules/` (6 roles) y `.cursor/skills/` (10 skills).
3. Revisa plantillas en `docs/templates/`.

---

## Cómo activar un rol

### Opción A — Mención en chat
```
@product_manager
Actúa como Product Manager. [tu instrucción]
```

### Opción B — Prompt + rule
Copia un prompt de `prompts/` y añade: "Sigue la rule [rol] en `.cursor/rules/`."

### Opción C — Skills
Para tareas técnicas específicas, invoca la skill:
```
Usa la skill flutter_feature para implementar T-030 según TASKS.md
```

---

## Flujo: Proyecto nuevo (ejemplo completo)

### 1. Preparar documentación
Copia `docs/templates/*.template.md` a `docs/` y adapta al proyecto (o usa los `docs/` existentes para Barbería App).

### 2. Product Manager
```
@product_manager
[prompts/new_project.md con tu idea]
```
→ Actualiza `docs/SPEC.md`  
→ **Aprueba SPEC con el usuario humano**

### 3. Architect
```
@architect
Lee docs/SPEC.md. Diseña arquitectura Clean Architecture.
Actualiza docs/ARCHITECTURE.md y docs/TASKS.md.
```
→ Stack, módulos, tareas `T-001`, `T-002`…

### 4. Developer (una tarea por sesión)
```
@developer
Usa skill flutter_feature si aplica.
Implementa T-001 según TASKS.md, SPEC y ARCHITECTURE.
No avances a tareas futuras.
```
→ Código en `projects/<nombre>/`  
→ Marca `[x]` en `TASKS.md`  
→ Entrada en `CHANGELOG.md`

### 5. QA
```
@qa
Valida MVP contra docs/SPEC.md.
Genera docs/QA_REPORT.md.
```
→ Skill `testing` si necesitas más cobertura

### 6. Reviewer
```
@reviewer
Revisa cambios. Genera docs/REVIEW.md.
```
→ Skill `code_review`

### 7. Security
```
@security
[prompts/security_audit.md]
Genera docs/SECURITY_REPORT.md.
```

### 8. Entrega
Veredictos en `QA_REPORT.md`, `REVIEW.md`, `SECURITY_REPORT.md`.

---

## Flujo: Proyecto existente

1. `project_analysis` → `docs/PROJECT_ANALYSIS.md`
2. `@product_manager` + `prompts/analyze_existing_project.md`
3. `@architect` → alinear `ARCHITECTURE.md`
4. Continuar Developer → QA → Reviewer → Security

---

## Documentos por rol

| Documento | Rol |
|-----------|-----|
| `SPEC.md` | Product Manager |
| `ARCHITECTURE.md`, `TASKS.md` | Architect |
| `projects/`, `CHANGELOG.md` | Developer |
| `QA_REPORT.md` | QA |
| `REVIEW.md` | Reviewer |
| `SECURITY_REPORT.md` | Security |
| `PROJECT_ANALYSIS.md` | Skill project_analysis |

---

## Buenas prácticas

1. **Un rol por sesión** — evita mezclar PM y Developer.
2. **Aprueba SPEC antes de arquitectura** — reduce retrabajo.
3. **Una tarea TASKS.md por sesión Developer** — diffs revisables.
4. **SDD antes de código** — Developer explica requisito, archivos y riesgos.
5. **Skills para workflows repetibles** — no reescribir instrucciones.
6. **Documenta siempre** — fuente de verdad en `docs/`.

---

## Ejemplo: Barbería App

```
1. SPEC.md     — citas, clientes, barberos, admin (ya definido)
2. ARCHITECTURE — Flutter + Riverpod + GoRouter + FastAPI + PostgreSQL
3. T-001       — base arquitectónica Flutter
4. T-002…      — auth, citas, servicios (incremental)
5. QA_REPORT   — validar US-001, RN-01…
6. REVIEW      — Clean Architecture, tests
7. SECURITY    — JWT, roles, validación inputs
```

---

## Más información

- [docs/SOFTWARE_FACTORY_WORKFLOW.md](docs/SOFTWARE_FACTORY_WORKFLOW.md)
- [docs/CLEANUP_REPORT.md](docs/CLEANUP_REPORT.md) — migración desde framework Python
