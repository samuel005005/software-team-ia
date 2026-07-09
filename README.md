# Software Factory — Cursor AI Team

Plantilla reutilizable para construir software con **Cursor + IA** de forma ordenada. No trae código de producto: trae **metodología**, **roles**, **skills** y un **orquestador** que ejecuta tareas desde la terminal.

```
Idea  →  SPEC  →  ARCHITECTURE  →  TASKS  →  projects/  →  QA / Review / Security
```

---

## ¿Qué es este sistema?

**No es una aplicación.** Es una **fábrica de software**: un equipo de IA + documentación + automatización para construir cualquier producto en `projects/`.

> Analogía: una constructora con planos obligatorios. **SPEC** = lo que el cliente quiere · **ARCHITECTURE** = cómo se construye · **TASKS** = cronograma · **Rules/Skills** = estándares de la empresa · **Factory** = el capataz que asigna la siguiente tarea · **projects/** = la obra.

**Tú defines qué quieres** (en chat y luego en `SPEC.md`). La IA diseña y ejecuta. El factory automatiza la ejecución tarea por tarea.

### Las 4 capas

```
┌─────────────────────────────────────────────────────────┐
│  1. HUMANO — idea, aprobaciones, prioridades            │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│  2. DOCUMENTOS (docs/) — SPEC, ARCHITECTURE, TASKS…     │
│     Fuente de verdad del proceso                        │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│  3. EQUIPO IA — rules (roles) + skills (know-how)       │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│  4. EJECUCIÓN — Cursor manual  O  factory (automático) │
│     → código en projects/                               │
└─────────────────────────────────────────────────────────┘
```

### Nomenclatura — IDs que verás en los docs

| Prefijo | Significa | Ejemplo | Dónde vive |
|---------|-----------|---------|------------|
| **US-XXX** | **User Story** — historia de usuario (qué quiere hacer alguien) | US-005: Reservar cita | `docs/SPEC.md` |
| **RN-XX** | **Regla de Negocio** — lógica que el sistema siempre debe cumplir | RN-01: Sin doble reserva | `docs/SPEC.md` |
| **T-XXX** | **Tarea** — trabajo técnico para implementar | T-001: Crear estructura base | `docs/TASKS.md` |
| **BUG-XXX** | Bug reportado en QA | BUG-001 | `docs/QA_REPORT.md` |

Relación típica:

```
SPEC:  US-005 "Reservar cita"  +  RN-01 "Sin doble reserva"
         ↓
TASKS: T-053 implementar endpoint, T-054 pantalla Flutter
         ↓
Código en projects/  →  QA valida US y RN con tests
```

### Los 6 roles (rules)

Cada rol es un agente con permisos y entregables definidos en `.cursor/rules/`.

| Rule | Rol | Escribe en | No toca |
|------|-----|------------|---------|
| `product_manager` | Product Owner | `docs/SPEC.md` | Código |
| `architect` | Arquitecto | `docs/ARCHITECTURE.md`, `docs/TASKS.md` | Código |
| `developer` | Developer | `projects/`, tests | SPEC sin aprobación |
| `qa` | QA Engineer | `docs/QA_REPORT.md` | Código de producción |
| `reviewer` | Tech Lead | `docs/REVIEW.md` | Código (solo reporta) |
| `security` | Security | `docs/SECURITY_REPORT.md` | Código de producción |

Activar en Cursor: `@product_manager`, `@architect`, `@developer`, etc.

### El factory — qué hace y por qué importa

El **factory** (`python -m factory`) no reemplaza Cursor: es el **director de orquesta** que:

1. Lee `docs/TASKS.md` — siguiente tarea pendiente
2. Lee `docs/SPEC.md` — criterios de la historia de usuario
3. Carga la **rule** del rol (Developer, QA…)
4. Sugiere **skills** según el tipo de trabajo
5. Arma un prompt completo y lo envía al **Cursor SDK**
6. El agente implementa, prueba y actualiza docs

```
TASKS.md + SPEC.md  →  factory/prompt_builder  →  Cursor SDK  →  projects/
                              ↓
                    Analizar → Crear → Probar → [x] en TASKS.md
```

| Sin factory | Con factory |
|-------------|-------------|
| Copias prompts a mano | Prompt armado automáticamente |
| Puedes saltarte el SPEC | Inyecta US + criterios en cada tarea |
| Progreso informal | `TASKS.md` es la cola de trabajo |
| Un rol por sesión | `pipeline` encadena Dev → QA → Review |

**Requisito:** Cursor Desktop abierto + `CURSOR_API_KEY` en `.env`.

### Flujo del equipo (SDD)

```
Idea (humano)
  ↓
Product Manager     →  docs/SPEC.md        (QUÉ: US, RN)
  ↓
Architect           →  docs/ARCHITECTURE.md + docs/TASKS.md  (CÓMO, en tareas)
  ↓
Developer           →  projects/           (código + tests)
  ↓
QA                  →  docs/QA_REPORT.md
  ↓
Reviewer            →  docs/REVIEW.md
  ↓
Security            →  docs/SECURITY_REPORT.md
  ↓
Entrega
```

Modo **manual** (Cursor) para SPEC y arquitectura. Modo **factory** para ejecutar muchas tareas seguidas.

### Qué NO es

| No es | Es |
|-------|-----|
| Una app lista para usar | Metodología + automatización |
| Un reemplazo de Cursor | Capa encima de Cursor |
| Un LLM propio | Usa modelos de Cursor (Composer, etc.) |
| CI/CD o deploy | Orquesta desarrollo local |
| Jira / Linear | `TASKS.md` es el plan en markdown |

---

## Qué obtienes

| Pieza | Ubicación | Para qué sirve |
|-------|-----------|----------------|
| **Rules** (roles) | `.cursor/rules/` | Comportamiento del PM, Architect, Developer, QA… |
| **Skills** (workflows) | `.cursor/skills/` | Clean Architecture por stack (Flutter, backend, tests…) |
| **Prompts** | `prompts/` | Instrucciones listas para Agent Mode |
| **Documentos SDD** | `docs/` | Requerimientos, diseño, plan de trabajo, reportes |
| **Orquestador** | `factory/` | Automatiza tareas de `docs/TASKS.md` vía Cursor SDK |
| **Código** | `projects/` | **Tú lo creas** — aquí vive tu app/API |

---

## Requisitos

- [Cursor Desktop](https://cursor.com) instalado y **abierto** (el orquestador usa el bridge local)
- Python **3.11+**
- `CURSOR_API_KEY` en `.env` ([Cursor → Settings → API](https://cursor.com))

---

## Instalación (una vez por máquina)

```bash
git clone <este-repo>
cd software-team-ai

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-factory.txt

cp .env.example .env
# Edita .env y pon tu CURSOR_API_KEY

export $(grep -v '^#' .env | xargs)  # cargar variables en la sesión
```

---

## Cómo usarla — guía rápida

Hay **dos formas** de trabajar. Puedes mezclarlas.

### Modo A — Manual (Cursor IDE)

Ideal para definir SPEC, arquitectura y decisiones que requieren tu criterio.

1. Abre el repo en **Cursor**.
2. En el chat (Agent Mode), menciona el rol o copia un prompt:

```text
@product_manager
Lee prompts/new_project.md. Quiero una app de [tu idea].
Actualiza docs/SPEC.md.
```

```text
@architect
Lee docs/SPEC.md. Diseña la arquitectura y crea tareas T-001, T-002…
Actualiza docs/ARCHITECTURE.md y docs/TASKS.md.
```

```text
@developer
Usa la skill flutter_feature (o backend_feature).
Implementa solo T-001 según TASKS.md y ARCHITECTURE.md.
```

3. El agente lee las **rules** y **skills** automáticamente según el rol.

### Modo B — Automático (orquestador `factory`)

Ideal para ejecutar tareas repetitivas ya definidas en `docs/TASKS.md`.

```bash
# Ver qué falta
python -m factory pending

# Siguiente tarea: analizar → implementar → probar
python -m factory run next

# Una tarea concreta
python -m factory run T-001

# Autopilot (todas las pendientes)
python -m factory run

# Solo análisis (modelo smart) o solo código (modelo fast)
python -m factory analyze T-001
python -m factory task T-001 --use-analysis

# Roles de cierre
python -m factory role qa
python -m factory role reviewer
python -m factory role security

# Pipeline: N tareas dev + QA (+ review/security opcional)
python -m factory pipeline --max-tasks 3 --review --security
```

**Importante:** Cursor Desktop debe estar abierto. Si ves `Connection refused`, ábrelo y reintenta.

---

## Primer proyecto — paso a paso

### Paso 1 — Especificar qué construir

En Cursor con `@product_manager`:

- Describe usuarios, historias de usuario (US-001, US-002…) y criterios de aceptación.
- Resultado: `docs/SPEC.md` completo.
- **Aprueba el SPEC** antes de seguir.

Plantilla vacía: `docs/templates/SPEC.template.md`

### Paso 2 — Diseñar cómo construirlo

En Cursor con `@architect`:

- Elige stack (Flutter, FastAPI, etc.) y estructura de carpetas.
- Parte el trabajo en tareas pequeñas con ID (`T-001`, `T-002`…).
- Resultado: `docs/ARCHITECTURE.md` + `docs/TASKS.md`.

Formato de tarea en `TASKS.md` (el factory lo parsea):

```markdown
| T-001 | Crear estructura base en projects/mi-app | US-001 | Developer | `[ ]` |
```

Estados: `[ ]` pendiente · `[~]` en progreso · `[x]` completada · `[!]` bloqueada

### Paso 3 — Crear el código

```bash
# Ejemplo Flutter
cd projects && flutter create mi_app && cd ..

# Ejemplo API (estructura manual o con @developer + skill backend_feature)
mkdir -p projects/mi-api
```

Documenta las rutas en `docs/ARCHITECTURE.md` y en el README de cada proyecto.

### Paso 4 — Desarrollar tarea por tarea

```bash
python -m factory run next
```

Cada ejecución hace:

1. **Analizar** — lee US + criterios desde `SPEC.md` → `.factory/analysis/T-XXX.md`
2. **Crear** — implementa en `projects/`
3. **Probar** — corre tests del stack
4. **Cerrar** — marca `[x]` en `TASKS.md`, actualiza `CHANGELOG.md`

### Paso 5 — Validar y entregar

```bash
python -m factory role qa          # → docs/QA_REPORT.md
python -m factory role reviewer    # → docs/REVIEW.md
python -m factory role security    # → docs/SECURITY_REPORT.md
```

---

## Flujo de documentos

| Documento | Quién lo crea | Contenido |
|-----------|---------------|-----------|
| `docs/SPEC.md` | Product Manager | **Qué** debe hacer el producto (US, reglas RN) |
| `docs/ARCHITECTURE.md` | Architect | **Cómo** se construye (stack, carpetas, ADRs) |
| `docs/TASKS.md` | Architect → Developer | **Tareas** T-XXX con estado |
| `projects/<nombre>/` | Developer | Código fuente |
| `docs/CHANGELOG.md` | Todos | Historial de cambios |
| `docs/QA_REPORT.md` | QA | Validación contra SPEC |
| `docs/REVIEW.md` | Reviewer | Code review |
| `docs/SECURITY_REPORT.md` | Security | Auditoría de seguridad |

**Regla de oro:** el requerimiento vive en `SPEC.md`. No lo dupliques en código ni en TASKS sin referencia a una US.

---

## Proyecto existente (brownfield)

Si ya tienes código:

1. Copia el repo en `projects/<nombre>/`
2. En Cursor: usa la skill `project_analysis` → genera `docs/PROJECT_ANALYSIS.md`
3. PM completa `SPEC.md`; Architect alinea `ARCHITECTURE.md` y crea `TASKS.md` con lo que falta

---

## Estructura del repositorio

```
software-team-ai/
├── .cursor/
│   ├── rules/              # product_manager, architect, developer, qa…
│   └── skills/             # flutter_feature, backend_feature, testing…
├── factory/                # python -m factory
├── docs/
│   ├── SPEC.md             # ← rellenar
│   ├── ARCHITECTURE.md     # ← rellenar
│   ├── TASKS.md            # ← rellenar
│   └── templates/          # plantillas para copiar
├── prompts/                # prompts para Agent Mode
├── projects/               # ← tu código aquí
│   └── README.md
└── README_AI_WORKFLOW.md   # guía operativa detallada
```

---

## Skills por tipo de trabajo

| Skill | Cuándo usarla |
|-------|----------------|
| `project_analysis` | Onboarding de código existente |
| `feature_design` | Diseñar una feature y sus tareas |
| `flutter_feature` | Módulo Flutter (Clean Architecture) |
| `backend_feature` | API / capas backend |
| `database_change` | Migraciones y esquema |
| `bug_fix` | Corregir bug con regresión |
| `refactor` | Mejorar estructura sin cambiar comportamiento |
| `testing` | Añadir cobertura de tests |
| `code_review` | Revisión estructurada |
| `security_audit` | Auditoría de seguridad |

Invócalas en el chat: `Usa la skill backend_feature para T-003`.

---

## Configuración del orquestador

Modelos por tier en `.env` (opcional):

```bash
FACTORY_MODEL_SMART=composer-2.5        # PM, Architect, Review, Security, análisis
FACTORY_MODEL_FAST=composer-2.5-fast    # Developer, QA
FACTORY_MODEL_CHEAP=composer-2.5-fast   # tareas simples (--tier cheap)
```

Más detalle: [docs/ORCHESTRATOR.md](docs/ORCHESTRATOR.md)

---

## Problemas frecuentes

| Error | Solución |
|-------|----------|
| `Connection refused` | Abre **Cursor Desktop** |
| `CURSOR_API_KEY` no definida | `export $(grep -v '^#' .env \| xargs)` |
| `No hay tareas pendientes` | Revisa `docs/TASKS.md` — debe haber filas con `[ ]` o `[~]` |
| El factory no ve una tarea | Usa formato de tabla con 4 o 5 columnas y estado `` `[ ]` `` |
| Agente no encuentra proyecto | Crea carpeta en `projects/` y documéntala en `ARCHITECTURE.md` |

---

## Enlaces

- [README_AI_WORKFLOW.md](README_AI_WORKFLOW.md) — workflow y buenas prácticas
- [projects/README.md](projects/README.md) — bootstrap de proyectos
- [docs/SOFTWARE_FACTORY_WORKFLOW.md](docs/SOFTWARE_FACTORY_WORKFLOW.md) — metodología SDD completa
- [docs/ORCHESTRATOR.md](docs/ORCHESTRATOR.md) — referencia de comandos `factory`
