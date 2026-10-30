# C216-L1 — Sistemas Distribuídos

Repositório das atividades práticas da disciplina **C216 L1 — Sistemas Distribuídos**.

## Tecnologias utilizadas

- Python 3.11
- FastAPI
- Poetry
- Docker e Docker Compose
- PostgreSQL 16
- SQLAlchemy
- Alembic
- Pytest
- Ruff
- JavaScript, React e React DOM
- Vite e Tailwind CSS
- npm, Biome, Vitest, React Testing Library e Playwright

## Estrutura do projeto

```text
C216-L1/
├── frontend/             # Interface React independente (Prática 6)
├── backend/
│   ├── alembic/          # Migrações do banco
│   ├── database/         # Configuração e sessões SQLAlchemy
│   ├── models/           # Modelos ORM
│   ├── repositories/     # Operações com o banco
│   ├── routers/          # Endpoints da API
│   ├── schemas/          # Validação com Pydantic
│   ├── services/         # Regras de negócio
│   ├── tests/            # Testes automatizados
│   ├── Dockerfile
│   ├── alembic.ini
│   └── pyproject.toml
├── docker-compose.yml
├── .env.example
├── Makefile
└── README.md
```

## Funcionalidades

A aplicação disponibiliza uma API REST desenvolvida com FastAPI.

A API de alunos permite:

- Cadastrar alunos.
- Listar alunos cadastrados.
- Consultar um aluno pelo ID.
- Atualizar os dados de um aluno.
- Remover alunos.

Os dados são armazenados em um banco PostgreSQL por meio do SQLAlchemy.

## Configuração do ambiente

É necessário ter Python, Poetry e Docker instalados.

Clone o repositório e acesse a pasta do projeto.

Crie um arquivo `.env` na raiz, utilizando `.env.example` como referência.

Para o ambiente Docker local configurado na prática, utilize:

```dotenv
DATABASE_URL_DOCKER=postgresql+psycopg://postgres:postgres@db:5432/c216_db
```

As credenciais apresentadas são apenas para desenvolvimento local. O arquivo `.env` não deve ser enviado ao GitHub.

## Executando com Docker

Na raiz do projeto, execute:

```bash
docker compose up -d --build
```

Para verificar os containers:

```bash
docker compose ps
```

Para acompanhar os logs:

```bash
docker compose logs -f backend
```

A API ficará disponível em:

- http://localhost:8000
- http://localhost:8000/docs — Documentação Swagger

## Migrações do banco de dados

O projeto utiliza Alembic para controlar as alterações na estrutura do banco.

Após iniciar o PostgreSQL, execute:

```bash
docker compose exec backend sh -c "cd /app/backend && alembic upgrade head"
```

Esse comando aplica as migrações pendentes, criando as tabelas necessárias.

Para consultar a versão atual:

```bash
docker compose exec backend sh -c "cd /app/backend && alembic current"
```

As migrações existentes estão armazenadas em `backend/alembic/versions/`.

## Endpoints de alunos

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/alunos/` | Cadastrar aluno |
| GET | `/alunos/` | Listar alunos |
| GET | `/alunos/{aluno_id}` | Consultar aluno |
| PUT | `/alunos/{aluno_id}` | Atualizar aluno |
| PATCH | `/alunos/{aluno_id}` | Atualizar parcialmente |
| DELETE | `/alunos/{aluno_id}` | Remover aluno |

Exemplo de cadastro:

```json
{
  "nome": "Gabriel",
  "email": "gabriel@teste.com",
  "curso": "Engenharia da Computação"
}
```

## Testes automatizados

Os testes foram desenvolvidos com Pytest e utilizam um banco SQLite em memória, isolado do PostgreSQL de desenvolvimento.

Para instalar as dependências:

```bash
cd backend
poetry install --no-root
```

Para executar os testes, na raiz do projeto:

```bash
make test
```

Para verificar a qualidade e a formatação do código:

```bash
make lint
```

Na implementação da Prática 5, foram validados **16 testes automatizados**.

## Persistência de dados

O PostgreSQL utiliza um volume Docker para preservar os registros.

Foi validado que os dados cadastrados permanecem disponíveis após reiniciar ou recriar o container da API.

**Atenção:** o comando `docker compose down -v` remove os volumes e pode apagar os dados armazenados.

## Integração contínua

O repositório possui um workflow do GitHub Actions para executar testes e verificações de qualidade de código.

## Prática 5 — Persistência

Nesta prática foram implementados:

- Integração entre FastAPI e PostgreSQL.
- Mapeamento objeto-relacional com SQLAlchemy.
- Migrações de banco com Alembic.
- Separação das responsabilidades em routers, services e repositories.
- Operações CRUD persistentes.
- Testes automatizados com isolamento do banco.
- Configuração de conexão por variáveis de ambiente.
- Execução da API e do PostgreSQL com Docker Compose.

## Prática 6 — Frontend moderno

O frontend permite cadastrar, listar, buscar, editar e excluir alunos com os campos **nome**, **e-mail** e **curso**, acompanhando o domínio da API existente. A interface é responsiva, apresenta mensagens de sucesso, erros associados aos campos e um diálogo de confirmação antes de excluir. É possível cancelar edições e exclusões; o diálogo também fecha com Escape.

Os dados existem somente no estado local do React. A lista começa vazia e é reiniciada ao recarregar ou fechar a página. Não há consumo de API, localStorage, sessionStorage ou banco de dados no frontend. As abas funcionam como sessões independentes.

### Tecnologias e estrutura

O projeto usa JavaScript (sem TypeScript), React/React DOM, Vite e Tailwind CSS com o plugin oficial para Vite. O npm gerencia as dependências; `frontend/package-lock.json` fixa a instalação reproduzível por `npm ci`. Biome verifica lint, formatação e organização de imports, com regras recomendadas habilitadas.

```text
frontend/
├── src/
│   ├── components/
│   │   ├── AlunoForm.jsx       # Cadastro, edição e erros dos campos
│   │   ├── AlunoList.jsx       # Listagem, estado vazio e ações
│   │   └── DeleteDialog.jsx    # Confirmação de exclusão
│   ├── App.jsx                # Estado em memória e coordenação dos fluxos
│   ├── validation.js          # Validação e normalização por funções puras
│   ├── index.css              # Tailwind e estilos globais
│   └── main.jsx               # Entrada React
├── tests/
│   ├── unit/                  # Validações e componentes isolados
│   ├── integration/           # Formulário, lista e operações em conjunto
│   ├── e2e/                   # Fluxos no navegador real
│   └── setup.js               # jest-dom, limpeza e adaptações do jsdom
├── biome.json
├── vite.config.js             # Vite e Vitest; E2E separado do Vitest
├── playwright.config.js       # Servidor automático e projetos desktop/celular
├── index.html
├── package.json
└── package-lock.json
```

Os campos são obrigatórios e não aceitam apenas espaços. O e-mail deve ter um formato válido. Os limites acompanham o modelo do backend: nome e curso até 100 caracteres e e-mail até 150. O frontend remove espaços externos e normaliza o e-mail para minúsculas. Não há regra de unicidade de e-mail, assim como no modelo atual da API.

### Executar o frontend

Pré-requisitos: **Node.js 24 LTS**, npm e, opcionalmente, GNU Make. O backend, o PostgreSQL e o Docker não precisam estar em execução para usar esta interface.

Na raiz do repositório:

```bash
make frontend-install
make frontend-dev
```

Abra o endereço informado pelo Vite, normalmente `http://localhost:5173`. Encerre com Ctrl+C.

Sem Make, inclusive no PowerShell:

```bash
cd frontend
npm ci
npm run dev
```

Se a política de execução do PowerShell bloquear `npm.ps1`, use `npm.cmd` nos mesmos comandos. Os alvos Make também aceitam `NPM=npm.cmd`.

### Qualidade, testes e build

| Na raiz do projeto | Dentro de `frontend/` | Finalidade |
|---|---|---|
| `make frontend-test` | `npm test` | Testes unitários e de integração com Vitest |
| `make frontend-e2e-install` | `npm run test:e2e:install` | Instalar Chromium, necessário uma vez por versão do Playwright |
| `make frontend-e2e` | `npm run test:e2e` | E2E desktop e celular com Playwright |
| `make frontend-lint` | `npm run lint` | Lint com Biome |
| `make frontend-format` | `npm run format` | Aplicar formatação |
| `make frontend-format-check` | `npm run format:check` | Verificar formatação sem modificar arquivos |
| `make frontend-check` | `npm run check` | Lint, formatação e organização de imports |
| `make frontend-build` | `npm run build` | Gerar build de produção em `frontend/dist/` |
| `make frontend-preview` | `npm run preview` | Servir o build para conferência local |

O Vitest utiliza jsdom, React Testing Library, jest-dom e user-event. Os testes cobrem validação de obrigatoriedade, e-mail, limites e normalização; formulário e listagem; cadastro, busca, edição, cancelamento e exclusão; e reinicialização do estado. Para desenvolvimento interativo, use `npm run test:watch`.

O Playwright inicia e encerra seu próprio servidor Vite na porta 5173, que deve estar livre. Os mesmos fluxos são executados em Chromium desktop e em viewport de celular, incluindo validações, confirmação, Escape, busca, recarga sem persistência e ausência de requisições de API. Não é necessário iniciar o servidor manualmente. Em Linux, a instalação completa do navegador e das dependências do sistema pode ser feita com `npx playwright install --with-deps chromium`.

O relatório E2E fica em `frontend/playwright-report/`; capturas e traces de falhas ficam em `frontend/test-results/`. Para abrir o relatório, execute `npx playwright show-report` em `frontend/`. Esses arquivos gerados, `node_modules/` e `dist/` são ignorados pelo Git.

Os comandos existentes do backend foram mantidos: `make test` executa Pytest e `make lint` executa Ruff. Seus testes continuam isolados do PostgreSQL, utilizando SQLite em memória.

### Integração contínua

O workflow `.github/workflows/frontend.yml` executa automaticamente em pushes para `pratica-6` e PRs destinados a `aulas` ou `pratica-6`, além de permitir disparo manual. Ele contém dois jobs:

1. `lint`: instala dependências com `npm ci` e verifica o lint com Biome.
2. `tests-and-format`: depende de `lint` por `needs`, verifica formatação e imports, executa Vitest e Playwright e gera o build de produção. Em caso de falha, publica os relatórios E2E como artefatos do workflow.

O workflow existente de backend também passa a executar nos pushes e PRs de `pratica-6`, preservando suas verificações de Pytest e Ruff. A execução remota dos workflows só ocorre após envio ao GitHub.

### Limitações e Prática 7

Esta prática entrega a interface e seus fluxos locais. Não há autenticação, sincronização de abas nem persistência dos cadastros no frontend. O backend e o PostgreSQL preservam seu funcionamento independente.

**A integração com o backend e a containerização do frontend ficam para a Prática 7**, incluindo o fluxo E2E integrado à API e ao banco. Nenhum container de frontend foi adicionado nesta etapa.
