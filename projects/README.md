# Proyectos

Aquí va el **código fuente** de cada producto. Este repositorio es la **fábrica** (metodología + IA); `projects/` es donde construyes.

## Estructura recomendada

```
projects/
├── mi-app/              # Frontend (Flutter, React, etc.)
├── mi-api/              # Backend (FastAPI, Nest, etc.)
└── mi-servicio/         # Otros (workers, lambdas, …)
```

Un solo monorepo o varias carpetas — documenta la convención en `docs/ARCHITECTURE.md`.

## Iniciar un proyecto nuevo

### 1. Especificación (Product Manager)

```text
@product_manager
Usa prompts/new_project.md con tu idea de producto.
Actualiza docs/SPEC.md.
```

### 2. Arquitectura (Architect)

```text
@architect
Lee docs/SPEC.md. Diseña stack y estructura.
Actualiza docs/ARCHITECTURE.md y docs/TASKS.md con tareas T-001, T-002…
```

### 3. Bootstrap del código (Developer)

Crea la carpeta bajo `projects/` según el stack elegido:

**Flutter (mobile):**
```bash
cd projects
flutter create mi_app
cd mi_app
flutter create . --platforms=android,ios   # si faltan plataformas
```

**FastAPI (backend):**
```bash
mkdir -p projects/mi-api
# Estructura domain/application/infrastructure/api — ver skill backend_feature
```

### 4. Desarrollo incremental

```bash
# Desde la raíz del repo
python -m factory run next
# o
python -m factory run T-001
```

### 5. Calidad y cierre

```bash
python -m factory role qa
python -m factory role reviewer
python -m factory role security
```

## Proyecto existente (brownfield)

1. Copia o clona el código en `projects/<nombre>/`
2. Ejecuta skill `project_analysis` → `docs/PROJECT_ANALYSIS.md`
3. PM actualiza `SPEC.md`; Architect alinea `ARCHITECTURE.md` y `TASKS.md`

## Convenciones

- **Una tarea = un incremento** en `docs/TASKS.md`
- **No mezclar productos** en la misma carpeta sin documentarlo
- **Tests** en cada proyecto (`pytest`, `flutter test`, etc.)
- **README** por proyecto con setup local y comandos de test

## Estado actual

| Proyecto | Descripción | Estado |
|----------|-------------|--------|
| _(ninguno)_ | Añade tu primer proyecto | — |
