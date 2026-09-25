# Painel de Inteligência de Mercado - Trads Corretora

Aplicação fullstack que responde: **em quais regiões do Brasil estão os melhores
mercados de plano de saúde e odonto, e para qual público?** Cruza dados do IBGE
(população, perfil etário, renda, empresas) com dados da ANS (beneficiários de
planos) para os 5.570 municípios.

Resposta ao [desafio técnico](https://github.com/Trads-Corretora/teste-junior)
da vaga de Programador Júnior I. Detalhes de arquitetura em
[`backend/ARQUITETURA.md`](./backend/ARQUITETURA.md).

## Sumário

1. [Como rodar](#como-rodar)
2. [O que foi construído](#o-que-foi-construído)
3. [Fontes de dados](#fontes-de-dados)
4. [Decisões técnicas](#decisões-técnicas)
5. [Análise do legado](#análise-do-legado)
6. [Limitações e próximos passos](#limitações-e-próximos-passos)
7. [Uso de IA](#uso-de-ia)

## Como rodar

Pré-requisito: Docker e Docker Compose.

```bash
cp .env.example .env                 
docker compose up -d --build          

# só na primeira vez (banco vazio):
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python -m app.ingestion.run
```

A ingestão baixa os dados do IBGE e da ANS e leva cerca de 1 a 2 minutos.

| O quê | Onde |
|---|---|
| Dashboard | http://localhost:5173 |
| API (docs interativas) | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

**Testes:** `docker compose run --rm backend pytest -v`


Com `make` instalado, há atalhos: `make up`, `make setup`, `make test`.

## O que foi construído

### Requisitos obrigatórios do desafio

- Análise do código legado, documentada na seção [Análise do legado](#análise-do-legado).
- Integração com a API do IBGE, consumida na ingestão dos dados.
- Persistência no PostgreSQL: a aplicação lê só do banco, nunca do IBGE por requisição.
- Consultas e filtros por estado, região e nome, com ordenação por vários critérios.
- Dashboard com cards de resumo e de destaque, gráfico de bolhas com 4 opções de eixo e ranking em 4 abas, todos atualizados pelos mesmos filtros.
- Docker: `docker compose up` sobe banco, backend e frontend.
- README com decisões, limitações e passo a passo para rodar.
- Repositório público, com histórico de commits que mostra a evolução.

### Diferenciais entregues

- Cruzamento com os dados da ANS, com beneficiários de plano médico e odontológico, que geram as métricas de adesão e de população sem plano.
- 36 testes automatizados de integração, com PostgreSQL real em banco isolado.
- CI no GitHub Actions, que roda os testes e o build do frontend a cada push ou pull request para a `main`.
- Paginação na listagem, validação dos parâmetros e mensagens de erro claras na ingestão.
- Atualização agendada dos dados: um container separado roda a ingestão todo mês.
- Uso de IA documentado na seção [Uso de IA](#uso-de-ia).

### Extras além do desafio

- `Makefile` com os comandos do dia a dia e documentação de arquitetura em [`backend/ARQUITETURA.md`](./backend/ARQUITETURA.md).


## Fontes de dados

Parti de 3 perguntas de negócio — tamanho do mercado, poder aquisitivo e perfil etário — e usei IA para buscar os agregados correspondentes no catálogo do IBGE. Todos foram conferidos na API antes de entrar.

| Pergunta | Fonte | Dado | Ano |
|---|---|---|---|
| Tamanho do mercado | IBGE agregado **6579** | População residente estimada | 2021 |
| Perfil etário | IBGE agregado **9515** | Índice de envelhecimento, idade mediana | 2022 |
| Poder aquisitivo | IBGE agregado **10289** | Rendimento médio e mediano do trabalho | 2022 |
| Poder aquisitivo | IBGE agregado **10295** | Renda domiciliar per capita (média e mediana) | 2022 |
| Mercado empresarial | IBGE agregado **1685** (CEMPRE) | Nº de empresas, pessoal assalariado, salários | 2021 |
| Cobertura de planos | **ANS** (taxa de cobertura) | Beneficiários de plano médico e de odonto | 2026 |

**Métricas calculadas** (no backend, ordenáveis pela API):
- **% de adesão** = beneficiários de plano médico ÷ população.
- **Sem plano médico / sem plano odontológico** = população − beneficiários.
- **Empresas e assalariados por mil habitantes.**


**Descartados:**
- **PIB dos Municípios (5938):** não tem PIB per capita pronto, e calculá-lo repetiria o erro do legado.
- **PNS (plano de saúde):** só cobre 27 capitais.

## Decisões técnicas

### Backend

- **Python**, pelo ecossistema maduro para dados: a mesma linguagem serve para a API e para a ingestão, que consome a API do IBGE e processa o CSV da ANS com bibliotecas simples como `requests` e `csv`.
- **FastAPI**, porque os parâmetros da API são validados por tipos com Pydantic (um critério de ordenação inválido, por exemplo, já volta como erro 422 sem código extra) e a documentação interativa em `/docs` é gerada automaticamente. A injeção de dependências entrega uma sessão de banco por requisição, e o `TestClient` facilita testar os endpoints de verdade.
- **SQLAlchemy 2.0** como ORM, que descreve as tabelas como classes Python tipadas, monta as consultas sem SQL escrito à mão (com parâmetros sempre vinculados, o que evita SQL injection) e alimenta o Alembic para gerar as migrations a partir dos models. Usei a versão síncrona, porque as consultas são de leitura simples e o assíncrono não traria ganho.
- A ingestão é executada via comando (`python -m app.ingestion.run`), separando a carga das requisições da API. Ela ocorre em etapas e usa **upsert** para evitar duplicidades. Em caso de falha, é feito **rollback** e o erro é exibido. Dados incompletos são ignorados com aviso.
- A atualização é agendada por um container separado, que usa a mesma imagem do backend e o APScheduler, com o intervalo configurável em `INGESTAO_CRON` (padrão: dia 1 de cada mês, às 03:00). Ele fica fora da API para não acoplar a carga, demorada e dependente de redes externas, ao ciclo de requisições, nem correr o risco de disparar em dobro com mais de um worker. O agendador executa uma ingestão por vez (`max_instances=1`), e uma falha é registrada em log e tentada de novo no próximo agendamento.
- A aplicação nunca consulta o IBGE nem a ANS por requisição: toda leitura vem do banco.

### Banco de dados

- Escolhi o **PostgreSQL** porque os dados são naturalmente relacionais, com um município ligado a vários indicadores, e porque ele guarda números com precisão exata. Ele também facilita a ingestão, já que o upsert nativo (`ON CONFLICT`) evita registros duplicados quando a carga roda de novo. E como uso o mesmo banco em desenvolvimento, testes e produção, o comportamento é o mesmo em todos os ambientes.
- Para acompanhar a evolução do schema desde a primeira tabela, entrou o **Alembic**: cada mudança vira uma migration versionada no Git, e dá para reverter uma delas se algo der errado.

### Frontend

- Para o frontend acabei escolhendo o Vue 3 com Vite, por ser leve e ter uma reatividade que combina com um dashboard: ao mudar um filtro, os cards, o gráfico e o ranking se atualizam sozinhos a partir da API.
- Para o gráfico de bolhas usei o Chart.js, que já oferece suporte nativo a esse tipo de visualização.

### Infraestrutura

- Com Docker Compose, banco, backend e frontend sobem com um único comando, sem exigir que quem avalia instale linguagem ou banco na máquina.

### Testes

- Optei por PostgreSQL real nos testes, em vez de SQLite, porque o projeto utiliza recursos específicos do Postgres, como Numeric, chaves estrangeiras e o ON CONFLICT. Assim, os testes refletem melhor o comportamento da aplicação em produção.
- Como são testes de integração, eles validam os endpoints junto ao banco. Para evitar interferência nos dados de desenvolvimento, utilizo um banco separado (db-test) em tmpfs, que inicia vazio e oferece execução rápida.

## Análise do legado

A pasta `legado/` trazia a tentativa de um ex-funcionário, o Rodrigo: um script PHP (`coleta_ibge.php` e `config.php`), um CSV exportado, um painel em HTML e um bilhete dizendo o que "já funcionava". O bilhete garantia que a coleta já salvava no banco, que o CSV estava "certinho e atualizado" e que existia um filtro de renda validado pela diretoria. Conferi tudo linha a linha, e quase nada disso se sustenta.

**`config.php`**
- Usa `mysql_connect`, uma extensão que foi removida do PHP na versão 7.0, em 2015. O script não roda em nenhuma versão atual.
- A senha do banco (`trads@123`) está escrita no próprio arquivo, com um comentário "depois eu faço" que nunca foi cumprido. A credencial fica exposta no histórico do repositório.

**`coleta_ibge.php`**
- Chama a API do IBGE na versão `v9`, que não existe. Segundo a documentação, a API é a v1 para localidades e a v3 para agregados.
- A função `pega_pib()` busca o PIB total do estado (agregado 5938, variável 37), mas o código trata o resultado como "renda per capita". São grandezas completamente diferentes: o PIB estadual está na casa dos bilhões de reais.
- Por causa desse erro, o filtro da linha 29 ("renda per capita menor que 2 salários mínimos") compara o PIB total com R$ 2.824, uma conta sem sentido.
- A função `salvar_no_banco()` não grava nada no banco. Ela só escreve um `.txt` local, então a afirmação do bilhete de que os dados "já são salvos na tabela `estados`" é falsa.
- O script só consulta estados, nunca municípios, embora o bilhete e o painel falem em municípios.

**`dados_exportados.csv`**

O bilhete o descreve como "certinho e atualizado", mas ele tem vários problemas, sem nenhum tratamento:
- uma linha duplicada (João Pessoa aparece duas vezes);
- encoding quebrado (`JoÃ£o Pessoa` em vez de "João Pessoa");
- formato numérico inconsistente, com população ora como `1234567`, ora como texto `"1.234.567"`;
- um registro absurdo, o "Município Fantasma", com 90 milhões de habitantes e renda de R$ 1.000;
- população negativa (Porto Alegre, `-1`);
- uma linha com coluna extra (`Curitiba;...;extra`);
- cabeçalho fora da ordem descrita no bilhete (`renda;populacao_total`, em vez de `populacao;renda_media`).

**`painel_antigo.html`**
- O botão "Atualizar dados" chama a API do IBGE direto do navegador, sem backend nem banco no meio. Isso vai contra o requisito central do desafio, que é persistir os dados e servir as consultas a partir do próprio banco: a cada clique, cada usuário dispara uma chamada à API pública, sem cache, sem controle de taxa e sem validar o que volta.
- Usa jQuery 1.7.2, de 2012, e declara `charset=ISO-8859-1` num arquivo com dados em UTF-8.
- Define a função `montaTabela()`, mas chama `montatabela()` (com "t" minúsculo) ao carregar a página. Esse erro de digitação impede que a tabela apareça sozinha.
- O endpoint usado em `carregaDados()` (`/v9/localidades/estados`) devolve estados, não a lista de municípios que o código espera. Mesmo que o endpoint existisse, o formato não bateria.

**Conclusão**

A análise mostrou que documentação, código e dados não conversam entre si. O código legado não persiste nada em banco, aponta para endpoints que não existem, confunde PIB estadual com renda per capita, e até o arquivo de dados "de confiança" é inconsistente.

## Limitações e próximos passos

**Limitações conhecidas**
- **Dados de anos diferentes.** Os dados obtidos pelo IBGE são do censo 2022. Já os dados obtidos pela ANS são do ano de referência de 2026.
- **Sem autenticação.** A API é somente leitura de dados públicos; a autenticação só faria sentido para proteger uma rota de reingestão ou ingestão, que não existe: o agendador roda em um container próprio, sem expor endpoint.

**O que faria com mais tempo**

1. Ampliaria as métricas, criando novos indicadores para identificar oportunidades de mercado a partir das diferentes fontes de dados.
2. Automatizaria a atualização das fontes, utilizando APIs, arquivos periódicos ou scraping quando necessário.
3. Implementaria monitoramento do pipeline, identificando automaticamente novas atualizações, falhas e inconsistências nos dados.
4. Evoluiria a arquitetura para ser mais robusta e escalável, com Redis para cachear as consultas mais acessadas ou mais pesadas e como fila de tarefas, movendo a ingestão para workers dedicados, mantendo a API isolada da carga de dados.

## Uso de IA

Usei o Claude como assistente durante o desenvolvimento. Registro
aqui como, para deixar claro o que foi decisão minha e o que a IA
sugeriu:

- **Leitura do legado:** pedi para a IA ler os pontos que eu tinha anotado
  sobre a analise dos arquivos da pasta `legado/` e apontar inconsistências 
  entre o que o bilhete do ex-funcionário afirmava e o que o código/dados 
  realmente faziam. Conferi cada ponto levantadom, endpoint da API, os problemas
  no CSV, pontos que "foram implementados", mas não foram.
- **Melhoria de texto:** a seção "A herança: análise do código legado"
  partiu de uma escrita inicial minha, com os pontos que eu já tinha
  levantado sobre o legado; pedi para a IA revisar e melhorar a
  redação, mantendo o conteúdo técnico que eu havia apurado. Conferi o 
  texto reescrito antes de aceitar.
- **Escolha dos agregados do IBGE:** mandei pra IA **3 perguntas de
  negócio minhas** (tamanho do mercado, poder aquisitivo, perfil
  etário) pra ela buscar agregados correspondentes no catálogo do
  IBGE — são milhares de tabelas, inviável vasculhar uma por uma na
  mão. A IA trouxe os 3 agregados e sugeriu por conta própria um
  4º, de mercado B2B/empresarial (CEMPRE). Avaliei essa sugestão e
  mantive, pela lógica de que a maioria dos planos de saúde no Brasil é
  coletivo via empregador. Depois conferi cada um dos 4 nos metadados
  reais da API (nível geográfico, período) e testei consulta de dado
  real em municípios específicos antes de decidir — inclusive descartei
  um agregado que a busca trouxe (Pesquisa Nacional de Saúde) depois de
  ver que só cobria 27 capitais, não os municípios.
- **IA como guia na implementação:** durante o desenvolvimento, a IA sugeria abordagens e implementações, e eu decidia o que ficava. Algumas sugestões aceitei por fazerem sentido pro projeto, outras descartei ou removi depois de avaliar que não compensavam no contexto. Também recorri à IA para revisar trechos do meu código, apontando problemas ou melhorias antes de commitar. Cada recomendação passava por mim antes de entrar no código.
