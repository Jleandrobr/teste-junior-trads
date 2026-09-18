# Stack

- Linguagem/framework: Python + FastAPI.
- ORM: SQLAlchemy 2.0.
- Banco: PostgreSQL.
- Infra: Docker + Docker Compose.


# Banco de dados

- ORM: SQLAlchemy
- Migrations: Gerenciados pelo Alembic


# Não esquecer de cadastrar as envs no gitignore

- Variáveis de ambiente via .env+ .env.example


# API

- Prefixo "/api/v1/" para os endpoints do backend.
- Filtros/ordenação.
- Padrões REST.


# IBGE

- Lembrar de que a cada requisição a aplicação busca os dados do banco e 
não da API do IBGE diretamente.
- Escolher os agregados que respondam 3 perguntas. Qual o tamanho do marcado? Qual renda média dessa população?
Qual a idade média da população? 


# Testes

- Biblioteca: Pytest.
- Banco de testes: Possibilidades de usar sqlite, mais leve e em memória.
Outra possibilidade é usar o Postgres usando um serviço temporario.


## Docker + Docker Compose

- Dockerfile: Docker na raiz do backend.
- docker-compose.yml na raiz do projeto com serviços: backend, db e frontend.

