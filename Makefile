PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
ALEMBIC := $(VENV)/bin/alembic
UVICORN := $(VENV)/bin/uvicorn

.PHONY: help venv install run test migrate makemigrations up up-d down logs clean

help:
	@echo "Targets:"
	@echo "  make venv            - create virtual environment"
	@echo "  make install         - install dependencies"
	@echo "  make run             - run API locally"
	@echo "  make test            - run pytest"
	@echo "  make migrate         - apply Alembic migrations"
	@echo "  make makemigrations  - create autogenerate migration"
	@echo "  make up              - start docker compose stack in foreground"
	@echo "  make up-d            - start docker compose stack in background"
	@echo "  make down            - stop docker compose stack"
	@echo "  make logs            - show docker compose logs"
	@echo "  make clean           - remove local caches and venv"

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(PYTEST) -q

migrate:
	$(ALEMBIC) upgrade head

makemigrations:
	$(ALEMBIC) revision --autogenerate -m "new migration"

up:
	docker compose up --build

up-d:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f

clean:
	rm -rf $(VENV) .pytest_cache .mypy_cache __pycache__ htmlcov
