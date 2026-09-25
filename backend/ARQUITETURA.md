# Decisões arquiteturais — backend

Este documento registra as decisões de arquitetura do backend e o estado
atual da implementação, como referência para o desenvolvimento e
justificativa das escolhas feitas no README.

## Stack

- **Linguagem/framework:** Python + FastAPI.
- **ORM:** SQLAlchemy 2.0 (estilo `Mapped`/`mapped_column`).
- **Banco:** PostgreSQL, com migrations em Alembic.
- **Agendamento:** APScheduler, em um container próprio.
- **Execução:** Docker + Docker Compose (desenvolvimento e produção).

## Fontes de dados

A partir de **3 perguntas de negócio do candidato** (tamanho do
mercado, poder aquisitivo, perfil etário — "onde e pra quem vender
plano"), usei IA pra buscar agregados correspondentes no catálogo do
IBGE. A IA sugeriu por conta própria um agregado de mercado B2B
(CEMPRE), que avaliei e mantive, pela lógica de que a maioria dos planos
de saúde no Brasil é coletivo via empregador. Depois entraram a renda
domiciliar per capita (agregado 10295) e os dados de beneficiários da
ANS, que cruzam a demanda potencial com a cobertura real.

Critério de escolha: responder direto uma das perguntas, chegar a
**município** e ser recente. Todos foram verificados na API real
(`/api/v3/agregados/{id}/metadados`) e testados com dado real de
município antes de entrar.

| Pergunta de negócio | Fonte | Variável(is) usada(s) | Ano na ingestão |
|---|---|---|---|
| Tamanho do mercado | IBGE **6579** — População residente estimada | `9324` | **2021** (2022 é ano de Censo, não existe estimativa) |
| Perfil etário do público | IBGE **9515** — Índice de envelhecimento, idade mediana, razão de sexo | `10612`, `10613`, `8845` | **2022** (Censo) |
| Poder aquisitivo (trabalho) | IBGE **10289** — Rendimento nominal médio/mediano do trabalho | `13536`, `13537` | **2022** (Censo) |
| Poder aquisitivo (per capita) | IBGE **10295** — Rendimento domiciliar per capita médio/mediano | `13431`, `13534` | **2022** (Censo) |
| Mercado B2B / plano coletivo | IBGE **1685** — CEMPRE: nº empresas, pessoal assalariado, salários | `367`, `708`, `662` | **2021** (último ano publicado) |
| Cobertura de planos | **ANS** — taxa de cobertura (CSV) | Beneficiários de plano médico e exclusivamente odontológico | **2026** |

**Descartados conscientemente:**

- **4938 e família (PNS "plano de saúde")** — parecia o dado mais
  direto, mas cobre só as **27 capitais**, não os 5.570 municípios.
- **5938 (PIB dos Municípios)** — não traz PIB per capita pronto, e
  calculá-lo repetiria o erro do legado.

**Decisão de design — um ano por fonte, gravado na tabela:** cada fonte
grava o ano que ela realmente tem (2021/2022 no IBGE, 2026 na ANS), em
vez de forçar um ano único. O descompasso é uma limitação documentada no
README, e manter o `ano` em cada tabela deixa o caminho aberto para
histórico.


## Modelagem de dados

```
estados               (id, sigla, nome, regiao)
municipios            (id, nome, estado_id → estados)
populacao             (municipio_id, ano, populacao)                          -- IBGE 6579
perfil_demografico    (municipio_id, ano, indice_envelhecimento,
                        idade_mediana, razao_sexo)                            -- IBGE 9515
renda                 (municipio_id, ano, rendimento_medio, rendimento_mediano,
                        rendimento_per_capita_medio,
                        rendimento_per_capita_mediano)                        -- IBGE 10289 e 10295
empresas              (municipio_id, ano, qtd_empresas,
                        pessoal_assalariado, salarios_mil_reais)              -- IBGE 1685
beneficiarios         (municipio_id, ano, qtd_beneficiarios_medicos,
                        qtd_beneficiarios_odonto)                             -- ANS
```

Uma tabela por fonte, cada uma com chave única `(municipio_id, ano)`,
o que sustenta o upsert da ingestão. A leitura faz `JOIN` entre as
tabelas por `municipio_id`, sem escolher "o ano mais recente" em tempo
de consulta, porque cada tabela já guarda só o ano ingerido. Valores
monetários usam `Numeric`, para não perder precisão.

## Estrutura de pastas

```
backend/
  app/
    main.py                  # instancia o FastAPI, CORS, registra routers e /health
    core/
      config.py              # settings via pydantic-settings (DATABASE_URL, INGESTAO_CRON)
    db/
      session.py             # engine, SessionLocal, Base, get_db() (dependency)
      models.py              # Estado, Municipio, Populacao, PerfilDemografico,
                             # Renda, Empresa, Beneficiario
    schemas.py               # DTOs Pydantic de resposta, separados dos models
    api/
      estados.py             # GET /api/v1/estados
      municipios.py          # GET /api/v1/municipios e /api/v1/municipios/resumo
    repositories/
      estado_repository.py      # leitura e upsert de Estado
      municipio_repository.py   # consulta com JOIN, filtros, ordenação e métricas derivadas
      indicador_repository.py   # upsert de população, perfil, renda, empresas e beneficiários
    services/
      indicadores_service.py    # regra do dashboard: listagem e resumo/destaques
      ingestao_service.py       # orquestra os clients e os repositories na gravação
    ingestion/
      localidades_client.py     # estados/municípios (API de Localidades do IBGE)
      ibge_client.py            # agregados do IBGE (API de Agregados/SIDRA)
      ans_client.py             # download e leitura do CSV de cobertura da ANS
      schemas.py                # validação (Pydantic) do que chega das fontes
      run.py                    # ponto de entrada da ingestão (script standalone)
      agendador.py              # agenda a ingestão com APScheduler (cron configurável)
  alembic/
    versions/                   # 3 migrations: tabelas iniciais, beneficiários, renda per capita
    env.py
  tests/
    api/                        # um arquivo de teste por router
    ingestion/                  # clients, ingestão e agendador
    conftest.py                 # banco de teste, fixtures e cliente HTTP
  requirements.txt
  alembic.ini
  Dockerfile
```

Estrutura em camadas: **rota → service → repository → model**.

- **Repository**: só acesso a dado (SQLAlchemy), sem regra de negócio.
  A leitura fica em `municipio_repository` (uma consulta compartilhada
  entre a listagem e o resumo) e a escrita da ingestão em
  `indicador_repository`.
- **Service**: regra de negócio e orquestração. `indicadores_service`
  monta a listagem e o resumo (totais, percentuais ponderados e
  destaques); `ingestao_service` decide como validar e persistir o que
  vem dos clients. A rota nunca chama o repository direto.
- **Router**: fino, recebe a request, chama o service e devolve o schema.

## Banco de dados / ORM

- SQLAlchemy **síncrono** (driver `psycopg2`), não assíncrono. Os
  endpoints são consultas de leitura simples sobre dados já persistidos,
  sem justificativa para a complexidade de `asyncpg`/`AsyncSession`.
- Sessão por requisição via dependency (`get_db`) do FastAPI.
- **Migrations:** Alembic desde a primeira tabela, em vez de
  `Base.metadata.create_all()`, que não deixa rastro da evolução do
  schema nem permite rollback. Hoje são três revisions: tabelas
  iniciais, tabela `beneficiarios` e colunas de renda per capita.
- **Upsert nativo** (`ON CONFLICT` do PostgreSQL) na gravação, para a
  ingestão poder rodar de novo sem duplicar registros.

## Ingestão de dados

- **Desacoplada do ciclo de request:** roda como script standalone
  (`python -m app.ingestion.run`), nunca por requisição do usuário. Isso
  corrige a falha do `painel_antigo.html`, que chamava a API do IBGE
  direto do navegador a cada clique.
- **Em etapas:** localidades, população, perfil demográfico, renda,
  empresas e beneficiários. Cada etapa é executada e registrada
  separadamente; em caso de falha há rollback e a mensagem do erro
  aparece no log. Registros incompletos são ignorados com aviso.
- **HTTP síncrono** (`requests`), consistente com o resto do backend,
  já que é um script batch e não um servidor concorrente.
- **Três fontes:** Localidades (`localidades_client.py`), Agregados/SIDRA
  (`ibge_client.py`) e o CSV da ANS (`ans_client.py`).
- Nas chamadas ao SIDRA, **`classificacao=` explícita** quando o agregado
  tem classificações (ex.: `10289` e `10295`), em vez de depender do
  default "Total" da API.
- **Validação com Pydantic** (`ingestion/schemas.py`) antes de persistir,
  corrigindo a falha do legado de assumir um formato de resposta que
  nunca bateu com o real.
- **Atualização agendada:** o `agendador.py` roda em um container à parte
  (mesma imagem do backend), com `CronTrigger` lido de `INGESTAO_CRON`
  (padrão: dia 1 de cada mês, às 03:00). Fica fora da API para não
  acoplar uma carga demorada e dependente de rede externa ao ciclo de
  requisições, nem disparar em dobro com mais de um worker. Usa
  `max_instances=1` e `coalesce=True`, e uma falha vai para o log e é
  tentada de novo no próximo agendamento.

## Configuração e segredos

- Variáveis de ambiente via `.env` (gitignorado) + `.env.example`
  commitado, carregadas com `pydantic-settings`. Corrige diretamente a
  senha hardcoded em `config.php` no legado.

## API

- Prefixo `/api/v1/` para os endpoints do backend (não confundir com o
  versionamento da API do IBGE), além do `/health`.
- `GET /api/v1/estados`: lista de estados, para os filtros.
- `GET /api/v1/municipios`: listagem paginada (`limite`, `offset`), com
  filtros por `estado`, `regiao` e `nome_municipio` (busca sem
  diferenciar acentos) e ordenação por `ordenar_por` e `direcao`.
- `GET /api/v1/municipios/resumo`: totais e destaques dos mesmos filtros,
  que alimentam os cards do dashboard.
- Os parâmetros são validados por tipos: um critério de ordenação
  inválido, por exemplo, volta como 422 do próprio FastAPI, sem
  handler de erro customizado.
- CORS liberado para a origem do frontend em desenvolvimento. Em
  produção, frontend e API ficam no mesmo domínio atrás do proxy, sem
  precisar de CORS.

## Testes

- **Política:** nenhuma funcionalidade é considerada concluída sem teste
  correspondente — endpoint novo, regra de filtro/ordenação ou parsing
  novo na ingestão entram no mesmo commit do seu teste.
- **Tipo:** testes de integração da API, com o `TestClient` do FastAPI
  batendo no endpoint e no banco de verdade, para pegar bugs entre as
  camadas. Os testes de ingestão mockam a chamada HTTP às fontes, para
  não depender das APIs reais.
- **Ferramenta:** `pytest` + `pytest-cov`.
- **Banco em teste:** PostgreSQL real, no serviço `db-test` (em `tmpfs`,
  isolado do banco de desenvolvimento), e não SQLite: o schema usa
  `Numeric`, chaves estrangeiras e `ON CONFLICT`, que o SQLite trata de
  outra forma.
- A estrutura de `tests/` espelha `app/api` e `app/ingestion`.

## Docker / Docker Compose

- `backend/Dockerfile`: `python:3.12-slim`, instala `requirements.txt` e
  copia `app/`, `alembic/` e `alembic.ini`. O comando padrão roda o
  `uvicorn` com `--reload`, para desenvolvimento.
- `docker-compose.yml` (desenvolvimento): `db`, `db-test`, `backend`,
  `agendador` e `frontend`. O banco tem volume nomeado e healthcheck, e
  os demais serviços esperam por ele (`service_healthy`).
- `docker-compose.prod.yml` (produção): `db`, `painel-api`,
  `painel-web` (build do Vue servido por nginx) e `agendador`, sem
  publicar portas nem subir o `db-test`. A API e o frontend entram na
  rede do proxy reverso, que encaminha `/api/*` para o backend.
- Objetivo: `docker compose up` sobe tudo sem exigir Python, Node ou
  Postgres instalados na máquina de quem avalia.

## Trade-offs assumidos / próximos passos

- **Sem autenticação:** a API é somente leitura de dados públicos e não
  expõe endpoint de ingestão; o agendador roda em container próprio.
- **Sem cache:** as consultas vão direto ao banco. Redis para cachear as
  mais acessadas ou pesadas, e como fila para mover a ingestão para
  workers dedicados, é o passo natural de escala.
- **Dados de anos diferentes:** IBGE de 2021/2022 e ANS de 2026, o que é
  uma limitação conhecida das fontes.
