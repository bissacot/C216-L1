POETRY = poetry
BACKEND = backend
DOCKER_COMPOSE = docker compose

.PHONY: help install test build up down logs ps restart

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

install:
	cd $(BACKEND) && $(POETRY) install

test:
	cd $(BACKEND) && $(POETRY) run pytest

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