.PHONY: up down migrate api test setup

up:
	docker compose up -d

down:
	docker compose down

migrate:
	alembic upgrade head

api:
	uvicorn app.main:app --reload --host 0.0.0.0 --port $${PORT:-8001}

test:
	pytest

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt
	cp -n .env.example .env || true
