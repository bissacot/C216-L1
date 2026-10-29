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

## Estrutura do projeto

```text
C216-L1/
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
