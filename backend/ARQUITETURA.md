# Decisões arquiteturais — backend

Este documento registra as decisões de arquitetura do backend antes da
implementação, para servir de referência durante o desenvolvimento e de
justificativa no README final.

## Stack

- **Linguagem/framework:** Python + FastAPI.
- **ORM:** SQLAlchemy 2.0 (estilo `Mapped`/`mapped_column`).
- **Banco:** PostgreSQL.
- **Execução:** Docker + Docker Compose.

## Fontes de dados do IBGE

A partir de **3 perguntas de negócio do candidato** (tamanho do
mercado, poder aquisitivo, perfil etário — "onde e pra quem vender
plano"), usei IA pra buscar agregados correspondentes no catálogo do
IBGE. A IA sugeriu por conta própria um 4º agregado (mercado B2B —
linha "Mercado B2B" abaixo), que avaliei e mantive, pela
lógica de que a maioria dos planos de saúde no Brasil é coletivo via
empregador. Critério de escolha (do candidato): responder direto uma
das perguntas, chegar a **município**, e ser recente — faz parte da
avaliação do desafio. Todos os 4 verificados na API real
(`/api/v3/agregados/{id}/metadados` e testados com dado real de
município antes de decidir).

| Pergunta de negócio | Agregado | Variável(is) usada(s) | Ano usado na ingestão |
|---|---|---|---|
| Tamanho do mercado | **6579** — População residente estimada | `9324` | **2021** (fallback — 2022 é ano de Censo, não existe estimativa) |
| Perfil etário do público | **9515** — Índice de envelhecimento, idade mediana, razão de sexo | `10612`, `10613`, `8845` | **2022** (Censo, único ano disponível) |
| Poder aquisitivo | **10289** — Rendimento nominal médio/mediano do trabalho | `13536` (médio), `13537` (mediano) | **2022** (Censo, único ano disponível) |
| Mercado B2B / plano coletivo | **1685** — CEMPRE: nº empresas, pessoal ocupado, salários | `367`, `708`, `662` | **2021** (último ano publicado) |

**Descartados conscientemente:**

- **4938 e família (PNS "plano de saúde")** — parecia o dado mais
  direto, mas verificado na API (`/agregados/4938/localidades/N6`)
  cobre só as **27 capitais**, não os 5.570 municípios.

**Decisão de design — ano de referência fixo, não "sempre o mais
recente":** em vez de ingerir sempre o último ano disponível por fonte
(o que resultaria em 2026/2022/2022/2021 — quatro anos diferentes na
mesma tela), a ingestão fixa **2022 como ano de referência**, com
fallback para o ano mais próximo quando a fonte não tem 2022 (só o
6579 precisa disso, cai para 2021; o 1685 já tem 2021 como seu ano mais
recente, então também bate). Resultado: só um descompasso de 1 ano
(2022 vs. 2021) em vez de um espalhado por 5 anos, e o dashboard não
precisa expor "ano de cada indicador" espalhado pela tela — um único
aviso de rodapé (dados de referência: 2021–2022) resolve.


## Modelagem de dados

```
estados               (id, sigla, nome, regiao)
municipios            (id, nome, estado_id → estados)
populacao             (municipio_id, ano, populacao)                          -- agregado 6579
perfil_demografico    (municipio_id, ano, indice_envelhecimento,
                        idade_mediana, razao_sexo)                            -- agregado 9515
renda                 (municipio_id, ano, rendimento_medio,
                        rendimento_mediano)                                   -- agregado 10289
empresas               (municipio_id, ano, qtd_empresas,
                        pessoal_assalariado, salarios_mil_reais)              -- agregado 1685
```

Uma tabela por fonte, cada uma com chave única `(municipio_id, ano)`.
`ano` fica na tabela (não hardcoded em outro lugar) para permitir
histórico no futuro, mas a ingestão hoje grava só o ano de referência
por fonte (2022, com fallback 2021 — ver "Fontes de dados do IBGE"). O
dashboard faz `JOIN` simples entre as quatro tabelas por `municipio_id`
— não precisa escolher "o ano mais recente" em tempo de consulta,
porque cada tabela já guarda só o ano de referência decidido na
ingestão.

## Estrutura de pastas

```
backend/
  app/
    main.py              # instancia o FastAPI, registra routers
    core/
      config.py          # settings via pydantic-settings (lê .env)
    db/
      session.py         # engine, SessionLocal, Base, get_db() (dependency)
      models.py          # Estado, Municipio, Populacao, PerfilDemografico, Renda, Empresa
    schemas.py            # DTOs Pydantic (request/response), separados dos models
    api/
      estados.py          # GET /api/v1/estados
      municipios.py       # GET /api/v1/municipios (filtros/ordenação)
      indicadores.py       # endpoints agregados para o dashboard
    repositories/
      estado_repository.py            # queries de Estado
      municipio_repository.py         # queries de Municipio (filtros/ordenação)
      indicador_repository.py         # queries de Populacao/PerfilDemografico/Renda/Empresa
    services/
      indicadores_service.py          # regra de negócio do dashboard (agregações, cálculos)
      ingestao_service.py             # orquestra ibge_client + repositories na gravação
    ingestion/
      localidades_client.py # busca estados/municipios (catálogo, API de Localidades)
      ibge_client.py        # chamadas HTTP aos 4 agregados (API de Agregados/SIDRA)
      run.py                # ponto de entrada da ingestão (script standalone)
  alembic/
    versions/              # migrations versionadas
    env.py
  tests/
    api/                    # espelha app/api — um arquivo de teste por router
    repositories/            # espelha app/repositories
    services/                 # espelha app/services
    ingestion/               # testes da ingestão (client + parsing)
  requirements.txt
  alembic.ini
  Dockerfile
  .env.example
```

Estrutura em camadas: **rota → service → repository → model**.

- **Repository**: só acesso a dado (queries SQLAlchemy), sem regra de
  negócio. Um por agregado de domínio (`Estado`, `Municipio`,
  indicadores).
- **Service**: regra de negócio e orquestração — ex.
  `IndicadoresService` decide como juntar população/perfil
  demográfico/renda/empresas por estado a partir do repository;
  `IngestaoService` decide como validar e persistir o que vem do
  `ibge_client`/`localidades_client`. Rota nunca chama repository
  direto.
- Router fica fino: recebe request, chama service, devolve schema de
  resposta.

Com repository e service separados desde o início, adicionar uma nova
fonte de dado ou uma nova regra de agregação não mexe nas rotas nem no
acesso a dado dos outros módulos — e cada camada fica testável
isoladamente (repository com banco de teste, service com repository
mockado).


## Banco de dados / ORM

- SQLAlchemy **síncrono** (driver `psycopg2`), não assíncrono. Os
  endpoints do dashboard são consultas de leitura simples sobre dados já
  persistidos — não há justificativa para a complexidade de
  `asyncpg`/`AsyncSession` nesse volume de I/O concorrente.
- Sessão por requisição via dependency (`get_db`) do FastAPI, padrão
  usual do ecossistema.
- **Migrations:** Alembic, desde a primeira tabela. A migration inicial
  já nasce junto com os models (`estados`, `municipios`, `populacao`,
  `perfil_demografico`, `renda`, `empresas`); qualquer mudança de schema
  depois disso vira uma nova revision, versionada e revisável no
  histórico do Git — em vez de `Base.metadata.create_all()`, que não
  deixa rastro de como o schema evoluiu nem permite rollback.

## Ingestão de dados do IBGE

- **Desacoplada do ciclo de request:** a ingestão roda como script
  standalone (`python -m app.ingestion.run`), não é disparada por
  requisição do usuário. Isso corrige diretamente a falha do
  `painel_antigo.html`, que chamava a API do IBGE direto do navegador a
  cada clique, sem cache nem controle.
- **HTTP síncrono** (`requests`), consistente com o resto do backend
  (que também é síncrono) — não há necessidade de `httpx` assíncrono
  para um script batch, não um servidor atendendo requisições
  concorrentes.
- Duas fontes de API diferentes: **Localidades** (`localidades_client.py`,
  catálogo de estados/municípios) e **Agregados/SIDRA**
  (`ibge_client.py`, os 4 indicadores).
- Nas chamadas ao SIDRA, **declarar `classificacao=` explicitamente**
  quando o agregado tiver classificações (ex.: `10289` tem Sexo e Cor
  ou raça) — a API assume "Total" se omitido, mas depender desse
  default implícito é frágil; melhor pedir explícito
  (`&classificacao=2[6794]|86[95251]`).
- Validação do formato de resposta da API com Pydantic antes de
  persistir — corrige a falha do legado de assumir um formato de
  resposta que nunca bateu com o real.
- Execução manual via `docker compose run backend python -m app.ingestion.run`
  durante o desenvolvimento/avaliação. Atualização agendada
  (cron/scheduler) fica como diferencial, não como parte do núcleo.

## Configuração e segredos

- Variáveis de ambiente via `.env` (gitignorado) + `.env.example`
  commitado, carregadas com `pydantic-settings`. Corrige diretamente a
  senha hardcoded em `config.php` no legado.

## API

- Prefixo `/api/v1/` para os endpoints do backend (não confundir com o
  versionamento da própria API do IBGE).
- Filtros/ordenação via query params (`?estado=PB&ordenar_por=populacao`).
  Filtro "por estado" resolvido via `JOIN` com `municipios.estado_id`
  (ver "Fontes de dados do IBGE" — sem ingestão separada em nível de
  estado).
- Erros de validação tratados pelo próprio FastAPI/Pydantic; sem
  handler de erro customizado além disso no núcleo.

## Testes

- **Política:** nenhuma funcionalidade é considerada concluída sem teste
  unitário correspondente — endpoint novo, regra de filtro/ordenação
  nova, ou parsing novo na ingestão, cada um entra na mesma
  PR/commit do seu teste, não depois.
- **Ferramenta:** `pytest` + `pytest-cov`. Testes de API usam o
  `TestClient` do FastAPI; testes de ingestão mockam a chamada HTTP ao
  IBGE (`respx`/`unittest.mock`) para não depender da API real.
- **Banco em teste:** Postgres real via `docker compose` (serviço
  `db-test` ou schema isolado), não SQLite em memória — o schema usa
  tipos/constraints específicos do Postgres e a ingestão será validada
  contra o mesmo banco de produção, para evitar teste passando com
  comportamento que diverge do real.
- Estrutura em `tests/` espelha `app/` (um arquivo de teste por
  router/módulo), para ficar óbvio o que ainda não tem cobertura.

## Docker / Docker Compose

- `backend/Dockerfile`: `python:3.12-slim`, instala `requirements.txt`,
  roda `uvicorn`.
- `docker-compose.yml` na raiz do projeto, serviços:
  - `db`: `postgres:16-alpine`, volume nomeado para persistência,
    healthcheck.
  - `backend`: build de `./backend`, `depends_on: db` (condição
    `service_healthy`), lê `DATABASE_URL` do `.env`.
  - `frontend`: adicionado quando essa etapa começar.
- Objetivo: `docker compose up` sobe banco + backend sem exigir Python
  ou Postgres instalados na máquina do avaliador.

## Trade-offs assumidos / próximos passos

- **Ingestão manual, não agendada** — atualização automática fica como
  diferencial, não como parte obrigatória.
