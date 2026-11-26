# C216 L1 — Prática 7 · Integração full stack

O sistema de gestão de alunos integra a interface React da Prática 6 à API FastAPI e ao PostgreSQL da Prática 5. A cada abertura da página, a interface consulta a turma cadastrada. O usuário pode filtrar por nome, e-mail ou curso, editar um aluno e confirmar ou cancelar sua exclusão.

## Inicialização com Docker Compose

Use o Docker com containers Linux e o Compose v2.24.4 ou superior (necessário para o ambiente de testes). Na raiz do projeto, execute no PowerShell:

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
docker compose up -d --build --wait
docker compose ps
```

| Serviço | Endereço local |
| --- | --- |
| Interface React | [Abrir gestão de alunos](http://localhost:5173) |
| API FastAPI | [Consultar saúde da API](http://localhost:8000/health) |
| Documentação interativa | [Abrir Swagger](http://localhost:8000/docs) |
| PostgreSQL | `localhost:5432` |

Para parar os serviços, execute `make down`. Para iniciá-los novamente com as mesmas imagens e dados, execute `make up`.

## Arquitetura

O Nginx serve os arquivos gerados pelo Vite. No navegador, o React usa `fetch` para acessar a API. O FastAPI valida o corpo com Pydantic, encaminha a operação ao serviço de alunos e acessa o PostgreSQL 16 pelo repositório SQLAlchemy. Dentro da rede do Compose, a API encontra o banco pelo nome `db`.

| Caminho | Responsabilidade |
| --- | --- |
| `frontend/src/App.jsx` e `components/` | Carregamento inicial com `useEffect`, estado da interface com `useState`, formulário, lista, filtro e diálogo |
| `frontend/src/services/` | Cliente HTTP, mensagens de erro e operações de alunos |
| `frontend/src/validation.js` | Campos obrigatórios, formato de e-mail, limites e normalização |
| `frontend/tests/{unit,integration,e2e}/` | Vitest, React Testing Library e Playwright |
| `backend/routers/` e `schemas/` | Endpoints FastAPI e contratos Pydantic |
| `backend/services/` e `repositories/` | Regras de negócio e operações com o banco |
| `backend/database/`, `models/` e `alembic/` | Sessões, modelo de aluno e histórico de migrações |
| `backend/tests/` | Testes unitários e de integração com Pytest |
| `docker-compose.yml` e `docker-compose.e2e.yml` | Serviços da aplicação e configuração isolada do E2E |
| `.github/workflows/` | Verificações do backend e do frontend |

O frontend usa JavaScript, React, Vite e Tailwind CSS. O backend usa Python (3.11 na imagem), Poetry, FastAPI, SQLAlchemy, psycopg e Alembic. Ruff e Biome verificam o código.

### Contrato dos alunos

| Método | Caminho | Uso |
| --- | --- | --- |
| GET | `/alunos/` | Carregar a lista ao abrir ou recarregar a página |
| POST | `/alunos/` | Cadastrar com nome, e-mail e curso, recebendo o ID atribuído pelo banco |
| GET | `/alunos/{id}` | Consultar os dados atuais antes da edição |
| PUT | `/alunos/{id}` | Salvar o formulário completo de edição |
| PATCH | `/alunos/{id}` | Atualizar apenas os campos enviados pela camada de serviços |
| DELETE | `/alunos/{id}` | Excluir após confirmação e receber HTTP 204 |

Os endpoints gerais das práticas anteriores continuam disponíveis em `/`, `/health`, `/saudacao/{nome}` e `/dobro/{numero}`. O formulário valida os dados antes do envio e conserva os valores digitados quando a gravação falha. Uma falha na listagem oferece nova tentativa. A lista e as mensagens de sucesso refletem a resposta da API.

## Variáveis de ambiente

O Compose lê o `.env` da raiz. O repositório inclui valores de exemplo para desenvolvimento em [.env.example](.env.example). Guarde credenciais reais no `.env` local, ignorado pelo Git.

| Variável | Finalidade |
| --- | --- |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Usuário, senha e banco utilizados na primeira inicialização de um volume vazio |
| `DATABASE_URL_DOCKER` | URL SQLAlchemy usada pelo Compose para definir `DATABASE_URL` no backend. Use o host `db` e as credenciais correspondentes ao volume |
| `DATABASE_URL` | URL lida diretamente pela API e pelo Alembic. Ao executar o backend no host, use `localhost` para o PostgreSQL publicado |
| `VITE_API_URL` | Endereço público da API, acessível pelo navegador. O padrão local é `http://localhost:8000` |
| `CORS_ORIGINS` | Origens completas autorizadas, separadas por vírgula. Os padrões incluem `localhost` e `127.0.0.1` nas portas 5173 (interface) e 4173 (preview) |

Para acessar a aplicação a partir de outra máquina, informe em `VITE_API_URL` o endereço da API visto por essa máquina e inclua a origem da interface em `CORS_ORIGINS`. Rode novamente `docker compose up -d --build --wait`, pois o Vite incorpora a URL ao JavaScript durante o build. O middleware CORS permite GET, POST, PUT, PATCH e DELETE com JSON e atende às requisições de preflight.

## Migrações e persistência

O Compose aguarda o healthcheck do PostgreSQL. A API executa `alembic upgrade head` antes de iniciar o Uvicorn. O frontend aguarda o healthcheck da API. Consulte a revisão aplicada ou reaplique as migrações pendentes com:

```powershell
docker compose exec backend python -m alembic -c backend/alembic.ini current
docker compose exec backend python -m alembic -c backend/alembic.ini upgrade head
```

O volume nomeado `postgres_data` preserva os registros ao recriar os containers no mesmo projeto Compose. Em instalações anteriores, mantenha o nome do projeto e as credenciais já utilizadas pelo volume. `docker compose down` preserva o volume. A opção `-v` o remove.

## Desenvolvimento e testes

Para usar os alvos locais, instale GNU Make, Python compatível com o projeto (3.10 ou 3.11), Poetry, Node.js 24 e npm. Mantenha o Docker em execução para o E2E. Na raiz do repositório:

```powershell
make install
make frontend-install
make frontend-e2e-install
make test-all
```

O comando `make test-all` executa Pytest, Vitest e Playwright. Em Windows, se necessário, use `make test-all NPM=npm.cmd`. Em Linux, para instalar também as bibliotecas do Chromium, execute `npx playwright install --with-deps chromium` em `frontend/`.

| Comando Make | O que executa |
| --- | --- |
| `make help` | Lista os comandos |
| `make build`, `make up`, `make down` | Constrói as imagens, inicia ou encerra os containers |
| `make ps`, `make logs`, `make restart` | Mostra o estado, acompanha logs ou reinicia os serviços |
| `make install`, `make test`, `make lint` | Instala as dependências com Poetry, executa Pytest ou verifica lint e formatação com Ruff |
| `make frontend-install`, `make frontend-dev` | Instala as dependências com npm ou inicia o Vite com recarga automática |
| `make frontend-test` | Executa os testes unitários e de integração com Vitest |
| `make frontend-e2e-install`, `make frontend-e2e` | Instala Chromium ou executa o E2E com a pilha completa |
| `make frontend-lint`, `make frontend-format-check`, `make frontend-check` | Verifica lint, formatação ou o conjunto de regras do Biome |
| `make frontend-format` | Aplica a formatação do frontend |
| `make frontend-build`, `make frontend-preview` | Gera o build em `frontend/dist/` ou serve o resultado localmente |
| `make test-all` | Executa todas as suítes de testes |

Para desenvolver com recarga automática, deixe a porta 5173 livre (`docker compose stop frontend` se a interface em container estiver ativa), execute `docker compose up -d --build backend` e então `make frontend-dev`. O Vite lê `VITE_API_URL` do ambiente ou do `.env` da raiz.

### Isolamento dos testes

- **Pytest** usa uma sessão SQLite em memória por teste de CRUD. Também verifica as rotas gerais e o CORS.
- **Vitest e React Testing Library** usam respostas HTTP simuladas para verificar formulários, serviços, carregamento, sucesso, erros HTTP, validação e indisponibilidade da API.
- **Playwright** inicia um projeto Compose com nome exclusivo, constrói o frontend, aplica as migrações e usa PostgreSQL 16 em `tmpfs`. As portas de loopback 15173 e 18000 precisam estar livres. O banco de teste só fica acessível na rede do projeto temporário. Os cenários usam cadastros exclusivos e exercitam CRUD, filtros, cancelamento, foco e recarga em Chromium desktop e emulação de celular. Ao terminar, o executor encerra o projeto de testes.

O relatório HTML fica em `frontend/playwright-report/`, com traces e capturas de falhas em `frontend/test-results/`. Abra o relatório com `npx playwright show-report` em `frontend/`.

### Conferência manual

1. Abra a [gestão de alunos](http://localhost:5173), cadastre um aluno de teste e busque pelo e-mail.
2. Recarregue a página. Localize o cadastro, altere o curso e confira o novo valor após outra recarga.
3. Abra a confirmação de exclusão, cancele e verifique que o aluno segue na lista. Confirme a exclusão do cadastro de teste e recarregue para verificar a remoção.

## Integração contínua

Os workflows de backend e frontend executam nos pushes de `pratica-7` e nos PRs destinados a `pratica-6`, `pratica-7` ou `aulas`, preservando os gatilhos anteriores. O backend roda Pytest e Ruff. O frontend executa Biome, Vitest, Playwright com o Compose isolado e o build Vite. O workflow do frontend publica os artefatos de diagnóstico em caso de falha.
