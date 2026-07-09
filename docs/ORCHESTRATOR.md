# Orquestador automático — Software Factory

Orquestador SDD basado en **Cursor SDK**. Ejecuta roles (Developer, QA, Reviewer, …) leyendo `docs/TASKS.md` y las rules/skills del repo.

## Requisitos

1. Python 3.11+
2. Dependencias: `pip install -r requirements-factory.txt`
3. Variable de entorno: **`CURSOR_API_KEY`** ([cursor.com](https://cursor.com) → Settings → API)

## Comandos

```bash
# Ver tareas pendientes
python -m factory pending

# Siguiente tarea Developer (marca [~] en TASKS.md)
python -m factory next

# TODO EN UNO: analizar + implementar + probar
python -m factory run T-051          # una tarea
python -m factory run                # TODAS las pendientes (autopilot)
python -m factory run --once         # solo la siguiente
python -m factory run --max 3        # máximo 3 tareas

# Solo análisis (smart) o solo implementación (fast)
python -m factory analyze T-051
python -m factory task T-051 --use-analysis

# Tarea específica (implementar + probar, sin análisis previo)
python -m factory task T-044

# Rol individual
python -m factory role qa
python -m factory role developer --instruction "Solo backend"

# Pipeline: 1 tarea dev + QA
python -m factory pipeline --max-tasks 1

# Pipeline completo (dev + QA + review + security)
python -m factory pipeline --max-tasks 1 --review --security

# Simular prompt sin API
python -m factory --dry-run next

# Modo silencioso (sin spinner ni progreso)
python -m factory --quiet next
```

### Progreso en tiempo real

Durante `next`, `task` o `role` verás:

- **Spinner** mientras el agente piensa o espera
- **Fases** (`▶ Iniciando agente`, `▶ Enviando instrucciones`)
- **Acciones** del agente (`Leyendo archivo`, `Ejecutando comando`, etc.)

Requisito: **Cursor Desktop abierto** (el SDK usa bridge local).

Si ves `Connection refused`, abre Cursor y reintenta.

## Flujo por requerimiento

Cada `factory task T-XXX` instruye al agente en **3 fases**:

1. **Analizar** — lee US + criterios de aceptación (inyectados desde `SPEC.md`)
2. **Crear** — implementa lo mínimo para cumplir el requerimiento
3. **Probar** — `pytest` / `flutter test` + verificación de criterios

Solo marca `[x]` en `TASKS.md` si la Fase 3 pasa.

### Comando único (recomendado)

```bash
# Una tarea
python -m factory run T-051

# Autopilot: todas las pendientes / en progreso (sin especificar ID)
python -m factory run

# Solo la siguiente
python -m factory run --once

# Límite de seguridad
python -m factory run --max 5
```

Ejecuta en secuencia:
1. **Análisis** (`smart`) → guarda `.factory/analysis/T-051.md`
2. **Implementar + probar** (`fast`) → usa el análisis previo

Re-ejecutar sin re-analizar:

```bash
python -m factory run T-051 --skip-analyze
```

## Flujo automático

```
docs/TASKS.md  →  factory (Python)  →  Cursor SDK Agent  →  código + docs
                      ↑
              .cursor/rules + prompts + skills
```

### Pipeline `pipeline`

1. **Developer** — implementa hasta `--max-tasks` pendientes
2. **QA** — si no quedan pendientes (o `--max-tasks 0`)
3. **Reviewer** — opcional (`--review`)
4. **Security** — opcional (`--security`)

## Estado

Cada ejecución real guarda historial en `.factory/state.json` (gitignored).

## Variables opcionales

| Variable | Default | Uso |
|----------|---------|-----|
| `CURSOR_API_KEY` | — | Obligatoria para ejecutar agentes |
| `FACTORY_MODEL` | `composer-2.5` | Fallback si no hay tier/rol |
| `FACTORY_MODEL_SMART` | = `FACTORY_MODEL` | PM, Architect, Reviewer, Security |
| `FACTORY_MODEL_FAST` | = `FACTORY_MODEL` | Developer, QA (implementación) |
| `FACTORY_MODEL_DEVELOPER` | — | Override solo Developer |
| `FACTORY_MODEL_ARCHITECT` | — | Override solo Architect |
| `FACTORY_CWD` | raíz del repo | Directorio local del agente |

### Modelo inteligente vs barato

En `.env` (ver también `.env.example`):

```bash
# Arquitectura y decisiones importantes
FACTORY_MODEL_SMART=composer-2.5

# Desarrollo normal
FACTORY_MODEL_FAST=composer-2.5-fast

# Tareas extremadamente simples
FACTORY_MODEL_CHEAP=composer-2.5-fast
```

| Tier | Variable | Roles por defecto |
|------|----------|-------------------|
| **smart** | `FACTORY_MODEL_SMART` | PM, Architect, Reviewer, Security |
| **fast** | `FACTORY_MODEL_FAST` | Developer, QA |
| **cheap** | `FACTORY_MODEL_CHEAP` | Solo con `--tier cheap` |

Forzar tier en una corrida:

```bash
python -m factory task T-072 --tier cheap    # tarea muy simple
python -m factory task T-050                 # usa fast (default dev)
python -m factory role architect --tier smart
```

Override fino por rol: `FACTORY_MODEL_DEVELOPER=...`, etc.

## Límites

- Requiere **API key** de Cursor (agentes en la nube/local vía SDK).
- **Aprobación humana** recomendada entre fases críticas (SPEC, merge).
- El agente debe marcar `[x]` en TASKS.md; el orquestador marca `[~]` al iniciar.
- No reemplaza CI: combina con GitHub Actions para tests automáticos.

## Integración CI (ejemplo)

```yaml
# .github/workflows/factory-next.yml
- run: pip install -r requirements-factory.txt
- run: python -m factory pipeline --max-tasks 1
  env:
    CURSOR_API_KEY: ${{ secrets.CURSOR_API_KEY }}
```
