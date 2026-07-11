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
Quiero una app de barbería: el cliente reserva cita, el barbero ve agenda.
Escribe docs/SPEC.md con US-001, US-002, criterios de aceptación y RN-01.
```

O con la plantilla de prompt:

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

# Siguiente tarea: analizar → implementar → probar (default)
python -m factory run

# Una tarea concreta
python -m factory run T-001

# Autopilot (todas las pendientes)
python -m factory run all

# Solo implementar (carga análisis previo si existe)
python -m factory task T-001

# Análisis: una tarea o grupal por US
python -m factory analyze T-001
python -m factory analyze US-001

# Ahorro de tokens
python -m factory run T-001 --skip-analyze    # sin fase Architect
python -m factory --full-prompt run T-001     # prompt completo (debug)

# Roles de cierre (con alcance opcional)
python -m factory role qa --phase "Fase 1"
python -m factory role qa --story US-001,US-002
python -m factory role qa --tasks T-001,T-002

# Release: QA + Review + Security + verificación automática
python -m factory release --phase "Fase 1"
python -m factory release --phase "Fase 1" --permissive

# Gate: solo lee reportes (sin agentes, ideal para CI)
python -m factory gate --require qa,reviewer,security
python -m factory gate --phase "Fase 1" --require qa,reviewer,security

# Fases definidas en TASKS.md
python -m factory phases

# Pipeline por fase (dev terminado + cierre)
python -m factory pipeline --max-tasks 0 --phase "Fase 1" --review --security
```

**Importante:** Cursor Desktop debe estar abierto. Si ves `Connection refused`, ábrelo y reintenta.

---

## Primer proyecto — paso a paso

### Paso 1 — Especificar qué construir

**Archivo:** `docs/SPEC.md` (fuente de verdad del producto).

No tienes que redactar todo a mano: cuéntale la idea al PM en Cursor y **tú apruebas** el resultado.

```text
@product_manager
Quiero una app de barbería: el cliente reserva cita, el barbero ve agenda.
Escribe docs/SPEC.md con US-001, US-002, criterios de aceptación y RN-01.
```

El PM debe dejar en `docs/SPEC.md` al menos:

| Elemento | Formato | Para qué sirve |
|----------|---------|----------------|
| **ID** | `### US-001 — Título` | `TASKS.md` referencia `US-001` |
| **Historia** | **Como** … **quiero** … **para** … | Contexto para Developer / QA |
| **Criterios** | lista con `- [ ]` | El agente valida contra esto |
| **Reglas** | `RN-01` en tabla | QA valida reglas de negocio |

Alternativa por terminal:

```bash
python -m factory role product_manager --instruction "App de barbería: reservas y agenda del barbero. Escribe SPEC con US y RN."
```

- Revisa `docs/SPEC.md` cuando el agente termine.
- **Aprueba el SPEC** antes de pasar al Architect.
- Plantilla vacía: `docs/templates/SPEC.template.md`

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

Tareas simples (sin fase Architect): `[skip-analyze]` en el título o columna `Análisis: skip`.

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
python -m factory run
```

Por defecto usa **prompts lean**, **sesión única** y reutiliza `.factory/analysis/` si existe.

Cada ejecución hace:

1. **Analizar** — lee US + criterios desde `SPEC.md` → `.factory/analysis/T-XXX.md`
2. **Crear** — implementa en `projects/`
3. **Probar** — corre tests del stack
4. **Cerrar** — marca `[x]` en `TASKS.md`, actualiza `CHANGELOG.md`
5. **Auto-validación** — si completaste la **última tarea de una fase** (`## Fase …`), ejecuta solo QA + Review + Security + gate (sin comando extra)

Para desactivar el paso 5: `python -m factory run --no-auto-release` o `FACTORY_AUTO_RELEASE=0` en `.env`.

### Paso 5 — Validar y entregar (manual, si hace falta)

Solo si desactivaste auto-release o quieres re-validar:

```bash
python -m factory release --phase "Fase 1"
python -m factory gate --phase "Fase 1" --require qa,reviewer,security
```

---

## ¿Cómo sabe el sistema que todo se cumple?

No es magia: hay **tres capas de verificación** que trabajan juntas.

### Capa 1 — Developer (por tarea)

Cada `factory run` obliga al agente a:

1. Leer criterios de aceptación de la US (desde `SPEC.md`)
2. Implementar solo lo necesario
3. **Ejecutar tests** (`pytest`, `flutter test`, etc.)
4. Marcar `[x]` en `TASKS.md` solo si la Fase 3 pasa

Si el agente marca `[x]` sin pruebas, QA lo detectará en el cierre.

### Capa 2 — Roles de cierre (agentes + reportes)

| Rol | Qué valida | Reporte | Veredicto esperado |
|-----|------------|---------|-------------------|
| **QA** | SPEC, criterios, RN, tests ejecutados | `docs/QA_REPORT.md` | **APROBADO** / CONDICIONAL / **RECHAZADO** |
| **Reviewer** | Arquitectura, código, tests | `docs/REVIEW.md` | **APROBADO** / **CAMBIOS REQUERIDOS** |
| **Security** | Auth, secretos, inputs, CVEs | `docs/SECURITY_REPORT.md` | **SEGURO** / RIESGOS / **INSEGURO** |

Los agentes **deben** escribir el veredicto en la sección `## Veredicto` del reporte (formato en las rules).

QA usa el prompt dedicado `prompts/qa_validate.md` y puede acotarse:

```bash
python -m factory role qa --phase "Fase 1"
python -m factory release --story US-003
```

### Capa 3 — Factory Gate (automático, sin LLM)

`factory gate` **lee los markdown** y las tareas del alcance:

```
┌─────────────────────────────────────────────────────────┐
│  1. ¿Todas las tareas del alcance están [x]?            │
│  2. ¿QA_REPORT.md dice **APROBADO**?                    │
│  3. ¿REVIEW.md dice **APROBADO**? (si se exige)         │
│  4. ¿SECURITY_REPORT.md dice **SEGURO**? (si se exige)  │
│  5. ¿Hay bugs CRITICAL abiertos en QA?                  │
└─────────────────────────────────────────────────────────┘
         ↓
   GATE ABIERTO  →  OK para merge/release
   GATE CERRADO  →  exit code 1 (útil en CI)
```

```bash
# Verificar sin gastar tokens
python -m factory gate --phase "Fase 1" --require qa,reviewer,security

# Modo permisivo (acepta CONDICIONAL / RIESGOS)
python -m factory gate --permissive --require qa
```

### Fases en TASKS.md

Agrupa tareas por milestone con encabezados `## Fase …`:

```markdown
## Fase 1 — Fundamentos

| T-001 | Setup API | US-001 | Developer | `[x]` |
| T-002 | Tests base | US-001 | Developer | `[x]` |
```

```bash
python -m factory phases                              # listar fases
python -m factory release --phase "Fase 1"            # cierre del milestone
python -m factory gate --phase "Fase 1" --require qa  # solo esa fase
```

### Flujo de release recomendado

```
Developer:  factory run (por tarea)
     ↓       → al marcar [x] la última tarea de una fase, auto-validación
     ↓       → QA + Review + Security + gate (FACTORY_AUTO_RELEASE=1)
     ↓
Humano:     merge si GATE ABIERTO
     ↓
CI:         factory gate --require qa,reviewer,security
```

Desactivar auto-validación: `--no-auto-release` o `FACTORY_AUTO_RELEASE=0`.

### Qué NO verifica el gate (todavía)

- No ejecuta tests por sí solo (eso lo hace el agente QA o tu CI)
- No lee cobertura de código
- No sustituye revisión humana en SPEC ni decisiones de producto

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
