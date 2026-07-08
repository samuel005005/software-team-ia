# Barbería API

Backend REST modular para Barbería App (FastAPI + PostgreSQL).

## Stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL 15+

## Desarrollo local

Ejecuta **un comando por línea** (no pegues comentarios `#` en la misma línea de `docker compose`).

```bash
cd projects/barberia-api

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env

docker compose up -d

alembic upgrade head

uvicorn app.main:app --reload --port 8001
```

Con Make (mismos pasos abreviados):

```bash
make setup
source .venv/bin/activate
make up
make migrate
make api
```

### URLs

| Recurso | URL |
|---------|-----|
| API | http://localhost:8001 |
| Docs | http://localhost:8001/docs |
| Health | http://localhost:8001/health |

### Puertos por defecto

| Servicio | Puerto host | Motivo |
|----------|-------------|--------|
| API | **8001** | Evita conflicto si ya usas 8000 |
| PostgreSQL | **5433** | Evita conflicto si ya usas 5432 |

Si necesitas otros puertos, edita `.env` (`PORT`, `DATABASE_URL`) y `docker-compose.yml`.

## Troubleshooting

### `no such service: #`

Pegaste un comentario en la misma línea (afecta a `docker compose`, `alembic`, `pytest`, etc.):

```bash
# ❌ Incorrecto
docker compose up -d          # PostgreSQL
alembic upgrade head          # aplica migraciones
pytest                        # 28 tests

# ✅ Correcto
docker compose up -d
alembic upgrade head
pytest
```

### `password authentication failed for user "barberia"`

PostgreSQL en **5432** es otro proyecto. Barbería usa **5433**:

1. Verifica que el contenedor esté arriba: `docker compose ps`
2. Confirma en `.env`: `DATABASE_URL=...@localhost:5433/barberia`
3. Si cambiaste credenciales, recrea el volumen: `docker compose down -v && docker compose up -d`

### `Address already in use` (puerto 8000)

Otro proceso usa 8000. Arranca en 8001:

```bash
uvicorn app.main:app --reload --port 8001
```

## Migraciones

```bash
alembic upgrade head
```

## Archivos de ignore

- `.gitignore` — Python, venv, `.env`, caches de tests
- `.dockerignore` — contexto limpio si se construye imagen Docker del API

## Tests

```bash
pytest
```

## Estado (Fase 1)

| Tarea | Estado |
|-------|--------|
| T-006 Esqueleto REST | ✅ |
| T-007 PostgreSQL + Alembic | ✅ |
| T-008 Enums y schemas base | ✅ |
| T-020..T-025 Modelo de datos | ✅ |
| T-030 Registro cliente | ✅ |
| T-031 Login + refresh JWT | ✅ |

Endpoints de negocio retornan `501 Not Implemented` hasta Fase 2/3.
