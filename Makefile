POETRY = poetry
BACKEND = backend

.PHONY: help install test

help:
	@echo "Comandos disponiveis:"
	@echo "  make install - Instala as dependencias do projeto"
	@echo "  make test    - Executa os testes"

install:
	cd $(BACKEND) && $(POETRY) install

test:
	cd $(BACKEND) && $(POETRY) run pytest