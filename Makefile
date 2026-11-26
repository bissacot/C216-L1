POETRY ?= poetry
NPM ?= npm
COMPOSE ?= docker compose
API_PORT ?= 8001

.PHONY: install api web test unit e2e browser lint build up down ps logs test-db migrate migration-current seed-demo demo demo-down

install:
	$(POETRY) -C backend install --no-root
	$(NPM) --prefix frontend ci

api:
	$(POETRY) -C backend run uvicorn app.main:app --host 127.0.0.1 --port $(API_PORT) --reload

web:
	$(NPM) --prefix frontend run dev

unit:
	$(POETRY) -C backend run pytest
	$(NPM) --prefix frontend test

browser:
	$(NPM) --prefix frontend run test:e2e:install

e2e:
	$(NPM) --prefix frontend run test:e2e

test: unit e2e

test-db:
	$(POETRY) -C backend run pytest tests/persistence

migrate:
	$(COMPOSE) exec -T api alembic upgrade head

migration-current:
	$(COMPOSE) exec -T api alembic current

seed-demo:
	$(COMPOSE) exec -T api python -m app.database.seed

lint:
	$(POETRY) -C backend run ruff check .
	$(POETRY) -C backend run ruff format --check .
	$(NPM) --prefix frontend run lint

build:
	$(NPM) --prefix frontend run build

up:
	$(COMPOSE) up -d --build --wait

down:
	$(COMPOSE) down

demo:
	$(COMPOSE) -f compose.yaml -f compose.demo.yaml --profile demo up -d --build --wait

demo-down:
	$(COMPOSE) -f compose.yaml -f compose.demo.yaml --profile demo down

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs --tail=100
