# Orquestador automático — Software Factory

Orquestador SDD basado en **Cursor SDK**. Ejecuta roles (Developer, QA, Reviewer, …) leyendo `docs/TASKS.md` y las rules/skills del repo.

## Requisitos

1. Python 3.11+
2. Dependencias: `pip install -r requirements-factory.txt`
3. Variable de entorno: **`CURSOR_API_KEY`** ([cursor.com](https://cursor.com) → Settings → API)

## Comandos

```bash
# Ver tareas pendientes (muestra flags skip-analyze / force-analyze)
python -m factory pending

# Siguiente tarea Developer — carga análisis compacto si existe
python -m factory next

# Recomendado: siguiente tarea con analyze + dev
python -m factory run              # default: solo la SIGUIENTE tarea
python -m factory run T-051        # una tarea concreta
python -m factory run all          # autopilot (todas)
python -m factory run --max 3      # máximo 3 tareas en autopilot

# Solo implementar (sin Architect) — usa análisis previo automáticamente
python -m factory task T-051

# Análisis
python -m factory analyze T-051    # una tarea
python -m factory analyze US-003   # grupal: todas las pendientes de esa US

# Flags de análisis
python -m factory run T-051 --skip-analyze      # ir directo a dev
python -m factory run T-051 --force-analyze     # re-analizar aunque exista archivo
python -m factory run all --no-batch-analyze    # sin pre-análisis grupal por US

# Optimización de tokens
python -m factory --lean run T-051              # prompts por referencia (default)
python -m factory --full-prompt run T-051       # inline rule + plantilla
python -m factory --no-single-session run T-051  # dos agentes (smart + fast)

# Rol individual / pipeline / dry-run
python -m factory role qa --phase "Fase 1"
python -m factory release --phase "Fase 1"
python -m factory gate --require qa,reviewer,security
python -m factory phases
python -m factory pipeline --max-tasks 0 --phase "Fase 1" --review --security
python -m factory --dry-run run T-051
```

### Progreso en tiempo real

Durante `next`, `task` o `role` verás:

- **Spinner** mientras el agente piensa o espera
- **Fases** (`▶ Iniciando agente`, `▶ Enviando instrucciones`)
- **Acciones** del agente (`Leyendo archivo`, `Ejecutando comando`, etc.)

Requisito: **Cursor Desktop abierto** (el SDK usa bridge local).

Si ves `Connection refused`, abre Cursor y reintenta.

## Ejecución secuencial

Todo es **secuencial** (sin paralelismo):

| Nivel | Comportamiento |
|-------|----------------|
| `run` | Por defecto **una** tarea; `run all` procesa en cola |
| Por tarea | Analyze → Dev (o sesión única con 2 mensajes) |
| `pipeline` | Dev → QA → Review → Security en serie |

## Optimización de tokens

| Mejora | Cómo |
|--------|------|
| **Prompts lean** (default) | Referencia `.cursor/rules/` y `prompts/` en lugar de inline |
| **Sesión única** (default) | Analyze + dev en **un agente**; el dev no re-explora el repo |
| **Análisis compacto** | Solo secciones clave inyectadas al Developer (máx. `FACTORY_MAX_ANALYSIS_CHARS`) |
| **Reutilizar análisis** | Si existe `.factory/analysis/T-XXX.md`, no re-analiza |
| **Análisis grupal** | En `run all`, 1 Architect por US con 2+ tareas → `_story_US-XXX.md` |
| **Marcadores en TASKS** | `[skip-analyze]` en título o columna `Análisis: skip` |
| **SPEC truncado** | `FACTORY_MAX_SPEC_CHARS` limita US inyectadas |

## Flujo por requerimiento

Cada `factory run T-XXX` (modo default con sesión única):

1. **Análisis** (smart) — plan en `.factory/analysis/T-XXX.md`
2. **Implementar + probar** (mismo agente) — sigue el plan sin repetir exploración

Modo `--no-single-session`: dos agentes (smart analyze, fast dev).

Solo marca `[x]` en `TASKS.md` si los tests y criterios pasan.

## TASKS.md — control de análisis

```
| T-080 | [skip-analyze] Ajustar README | US-001 | Developer | `[ ]` |
```

O columna opcional:

```
| ID | Tarea | Historia | Responsable | Análisis | Estado |
| T-090 | Setup | US-002 | Developer | skip | `[ ]` |
| T-091 | Feature | US-002 | Developer | force | `[ ]` |
```

## Flujo automático

```
docs/TASKS.md  →  factory (Python)  →  Cursor SDK Agent  →  código + docs
                      ↑
              .cursor/rules + prompts + skills
```

### Pipeline `pipeline`

1. **Developer** — hasta `--max-tasks` (0 = solo cierre)
2. **QA** — cuando el alcance no tiene tareas pendientes (`--phase` / `--story` / `--tasks`)
3. **Reviewer** — opcional (`--review`)
4. **Security** — opcional (`--security`)

### Release y Gate

| Comando | Qué hace |
|---------|----------|
| `factory release --phase "Fase 1"` | QA + Review + Security (agentes) y luego evalúa gate |
| `factory gate --require qa,reviewer,security` | Solo lee reportes y tareas (sin API, útil en CI) |

El **gate** comprueba:

1. Tareas del alcance en `[x]`
2. Veredicto en `## Veredicto` de cada reporte requerido
3. Bugs CRITICAL abiertos en QA

Veredictos esperados: QA **APROBADO** · Review **APROBADO** · Security **SEGURO**

`--permissive` acepta CONDICIONAL / RIESGOS.

## Estado

Cada ejecución real guarda historial en `.factory/state.json` (gitignored).
Análisis en `.factory/analysis/` (por tarea o `_story_US-XXX.md`).

## Variables opcionales

| Variable | Default | Uso |
|----------|---------|-----|
| `CURSOR_API_KEY` | — | Obligatoria para ejecutar agentes |
| `FACTORY_MODEL` | `composer-2.5` | Fallback si no hay tier/rol |
| `FACTORY_MODEL_SMART` | = `FACTORY_MODEL` | PM, Architect, Reviewer, Security |
| `FACTORY_MODEL_FAST` | = `FACTORY_MODEL` | Developer, QA (implementación) |
| `FACTORY_LEAN_PROMPT` | `1` | Prompts por referencia (ahorra tokens) |
| `FACTORY_SINGLE_SESSION` | `1` | Analyze + dev en un solo agente |
| `FACTORY_MAX_ANALYSIS_CHARS` | `4000` | Límite al inyectar análisis al dev |
| `FACTORY_MAX_SPEC_CHARS` | `6000` | Límite de US inyectadas desde SPEC |
| `FACTORY_AUTO_RELEASE` | `1` | QA+Review+Security+gate al completar fase |
| `FACTORY_AUTO_RELEASE_REVIEW` | `1` | Incluir Reviewer en auto-validación |
| `FACTORY_AUTO_RELEASE_SECURITY` | `1` | Incluir Security en auto-validación |
| `FACTORY_CWD` | raíz del repo | Directorio local del agente |

### Modelo inteligente vs barato

En `.env` (ver también `.env.example`):

```bash
FACTORY_MODEL_SMART=composer-2.5
FACTORY_MODEL_FAST=composer-2.5-fast
FACTORY_MODEL_CHEAP=composer-2.5-fast
FACTORY_LEAN_PROMPT=1
FACTORY_SINGLE_SESSION=1
```

| Tier | Variable | Roles por defecto |
|------|----------|-------------------|
| **smart** | `FACTORY_MODEL_SMART` | PM, Architect, Reviewer, Security |
| **fast** | `FACTORY_MODEL_FAST` | Developer, QA |
| **cheap** | `FACTORY_MODEL_CHEAP` | Solo con `--tier cheap` |

## Límites

- Requiere **API key** de Cursor (agentes en la nube/local vía SDK).
- **Aprobación humana** recomendada entre fases críticas (SPEC, merge).
- El agente debe marcar `[x]` en TASKS.md; el orquestador marca `[~]` al iniciar.
- No reemplaza CI: combina con GitHub Actions para tests automáticos.

## Integración CI (ejemplo)

```yaml
# .github/workflows/factory-gate.yml
- run: pip install -r requirements-factory.txt
- run: python -m factory gate --require qa,reviewer,security
```
