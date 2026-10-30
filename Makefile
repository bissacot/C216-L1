POETRY = poetry
BACKEND = backend
DOCKER_COMPOSE = docker compose
NPM = npm
FRONTEND = frontend

.PHONY: help install test lint build up down logs ps restart

help:
	@echo "Comandos disponiveis:"
	@echo "  make install - Instala as dependencias do projeto"
	@echo "  make test    - Executa os testes"
	@echo "  make build   - Constroi as imagens Docker"
	@echo "  make up      - Sobe os containers"
	@echo "  make down    - Para e remove os containers"
	@echo "  make logs    - Exibe os logs dos containers"
	@echo "  make ps      - Lista os containers do projeto"
	@echo "  make restart - Reinicia os containers"
	@echo "  make frontend-install - Instala dependencias do frontend"
	@echo "  make frontend-dev - Inicia o Vite"
	@echo "  make frontend-test - Executa testes unitarios e de integracao"
	@echo "  make frontend-e2e-install - Instala Chromium para E2E"
	@echo "  make frontend-e2e - Executa Playwright"
	@echo "  make frontend-lint - Verifica lint com Biome"
	@echo "  make frontend-format - Formata arquivos com Biome"
	@echo "  make frontend-format-check - Verifica formatacao"
	@echo "  make frontend-check - Verifica lint, formatacao e imports"
	@echo "  make frontend-build - Gera build de producao"
	@echo "  make frontend-preview - Serve o build de producao"

install:
	cd $(BACKEND) && $(POETRY) install

test:
	cd $(BACKEND) && $(POETRY) run pytest

lint:
	cd $(BACKEND) && $(POETRY) run ruff check
	cd $(BACKEND) && $(POETRY) run ruff format --check .

build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

ps:
	$(DOCKER_COMPOSE) ps

restart:
	$(DOCKER_COMPOSE) restart

.PHONY: frontend-install frontend-dev frontend-test frontend-e2e-install frontend-e2e frontend-lint frontend-format frontend-format-check frontend-check frontend-build frontend-preview

frontend-install:
	cd $(FRONTEND) && $(NPM) ci

frontend-dev:
	cd $(FRONTEND) && $(NPM) run dev

frontend-test:
	cd $(FRONTEND) && $(NPM) test

frontend-e2e-install:
	cd $(FRONTEND) && $(NPM) run test:e2e:install

frontend-e2e:
	cd $(FRONTEND) && $(NPM) run test:e2e

frontend-lint:
	cd $(FRONTEND) && $(NPM) run lint

frontend-format:
	cd $(FRONTEND) && $(NPM) run format

frontend-format-check:
	cd $(FRONTEND) && $(NPM) run format:check

frontend-check:
	cd $(FRONTEND) && $(NPM) run check

frontend-build:
	cd $(FRONTEND) && $(NPM) run build

frontend-preview:
	cd $(FRONTEND) && $(NPM) run preview
