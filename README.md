# Painel de Inteligência de Mercado - Trads Corretora

Aplicação fullstack para apoiar a decisão de **em quais regiões do Brasil
estão os melhores mercados, e para qual público**, a partir de dados
públicos do IBGE.

Desenvolvido como resposta ao [desafio técnico](https://github.com/Trads-Corretora/teste-junior)
para a vaga de Programador Júnior I.

## Stack

- **Backend:** Python + FastAPI
- **Banco de dados:** PostgreSQL
- **Frontend:** Vue.js
- **Infraestrutura:** Docker / Docker Compose

## Como rodar localmente

Pré-requisito: Docker + Docker Compose instalados.

```bash
# Configurar variáveis de ambiente (ajuste a senha)
cp .env.example .env

# Subir a aplicação inteira
docker compose up -d --build
```

Isso já deixa **banco + backend + frontend rodando**. Confirmar:
- `http://localhost:8000/health` deve responder `{"status": "ok"}`.
- `http://localhost:5173` deve abrir o dashboard (tabela ranking +
  gráfico de dispersão).

**Na primeira vez** (banco ainda vazio), rode também a criação das
tabelas e a carga inicial de dados do IBGE:

```bash
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python -m app.ingestion.run
```

**Rodar os testes automatizados:**

```bash
docker compose run --rm backend pytest -v
```

Se preferir, pode usar o `Makefile` (`make up`,
`make setup`, `make test` etc.) se tiver `make` instalado.


## A herança: análise do código legado

A pasta `legado/` do desafio original continha uma tentativa anterior de um
ex-funcionário chamado "Rodrigo", um script PHP (`coleta_ibge.php` +
`config.php`), um CSV exportado (`dados_exportados.csv`) e um painel HTML
(`painel_antigo.html`), acompanhados de um bilhete (`LEIA-ME-primeiro.txt`)
descrevendo o que "já funcionava".

O bilhete afirma que a coleta "já salva no banco", que o CSV está
"certinho e atualizado" e que existe um filtro de renda validado pela
diretoria. Verificando o código e os dados linha a linha, quase nenhuma
dessas afirmações se sustenta:

**`config.php`**
- Usa `mysql_connect`/`mysql_select_db`, extensão **removida do PHP desde a
  versão 7.0** (2015). O script não roda em nenhuma versão atual do PHP.
- Senha do banco (`trads@123`) hardcoded no arquivo, com um comentário
  "depois eu faço" que nunca foi cumprido, credencial exposta no
  histórico do repositório.

**`coleta_ibge.php`**
- Chama `https://servicodados.ibge.gov.br/api/v9/...`. A API real do IBGE
  é a **v1** para localidades (`/api/v1/localidades/estados`) e **v3**
  para agregados, segundo a documentação. O endpoint `v9` usado no script
  não existe.
- `pega_pib()` busca o agregado 5938 / variável 37, que corresponde ao
  **PIB total do estado**, mas o código trata e nomeia o resultado como
  "renda per capita". São grandezas completamente diferentes. O PIB
  estadual está na casa de bilhões de reais.
- O filtro na linha 29 "renda_per_capita < 2 salários mínimos" compara esse valor de PIB total
  com R$ 2.824. Uma comparação sem sentido semântico, herdada do erro
  acima.
- `salvar_no_banco()` **não grava no banco**: apenas escreve um `.txt`
  local via `file_put_contents`. A afirmação do bilhete de que os dados
  "já são salvos na tabela `estados`" é falsa.
- O script faz requisições apenas para o endpoint de **estado**, nunca de **município**,
  apesar do bilhete e do painel mencionarem municípios.

**`dados_exportados.csv`** — descrito como "certinho e atualizado", mas
contém, sem qualquer tratamento:
- uma linha duplicada (João Pessoa aparece duas vezes);
- encoding quebrado (`JoÃ£o Pessoa` em vez de "João Pessoa");
- formato numérico inconsistente (população ora `1234567`, ora
  `"1.234.567"` como texto com separador de milhar);
- um registro absurdo ("Município Fantasma", população de 90 milhões,
  renda de R$ 1.000);
- um valor de população negativo (Porto Alegre, `-1`);
- uma linha com coluna extra (`Curitiba;...;extra`);
- e a ordem de colunas no cabeçalho (`renda;populacao_total`) não bate
  com a ordem descrita no bilhete (`populacao;renda_media`).

**`painel_antigo.html`**
- O botão "Atualizar dados" chama `$.getJSON` **direto do navegador** para
  a API do IBGE, não existe backend nem banco no caminho. Isso contraria
  justamente o requisito central do desafio (persistir os dados e servir
  as consultas a partir do próprio banco, sem bater na API do IBGE a cada
  requisição do usuário): aqui cada usuário, a cada clique, gera uma
  chamada direta à API pública, sem cache, sem controle de taxa e sem
  validação do que volta.
- Usa jQuery 1.7.2 (2012), obsoleto, e declara `charset=ISO-8859-1` num
  arquivo com dados em UTF-8.
- Define a função `montaTabela()` mas chama `montatabela()` (minúsculo)
  no `$(document).ready`, um erro de digitação que impede a tabela de
  carregar automaticamente ao abrir a página.
- O endpoint chamado em `carregaDados()` (`/v9/localidades/estados`)
  retorna objetos de estado (UF), não um array de municípios com
  `[codigo, municipio, populacao, renda]` como o código assume, mesmo
  se o endpoint existisse, o formato não bateria com o que o script
  espera.

**Conclusão:** A analise do legado identificou inconsistências entre a documentação 
fornecida, implementação e dados exportados. O codigo legado não persiste dados em 
nenhum banco, aponta para endpoints que não existem, confunde PIB estadual com renda 
per capita, e o próprio arquivo de dados "de confiança" está inconsistente.

## Decisões técnicas

Detalhamento completo em [`backend/ARQUITETURA.md`](./backend/ARQUITETURA.md).
Resumo das escolhas principais:

**Fontes de dados do IBGE.** A partir de 3 perguntas de negócio minhas
(tamanho do mercado, poder aquisitivo, perfil etário — "onde e pra quem
vender plano"), usei IA pra buscar agregados correspondentes no
catálogo do IBGE; ela sugeriu por conta própria um 4º (mercado B2B),
que avaliei e mantive. Todos verificados na API antes de decidir:

| Pergunta | Agregado | O que traz |
|---|---|---|
| Tamanho do mercado | **6579** | População residente estimada |
| Perfil etário | **9515** | Índice de envelhecimento, idade mediana |
| Poder aquisitivo | **10289** | Rendimento médio/mediano do trabalho (Censo 2022) |
| Mercado B2B | **1685** | CEMPRE — nº empresas, pessoal ocupado, salários |

Descartei o **PIB dos Municípios (5938)** — não tem PIB per capita
pronto, calcular via `PIB ÷ população` repetiria o erro do legado — e a
**PNS "plano de saúde"**, que só cobre 27 capitais, não os 5.570
municípios.



## Principal vs. extra

**Núcleo (pedido pelo desafio):**
- Análise do legado.
- Integração real com a API do IBGE.
- Persistência dos dados no Postgres, aplicação consulta o próprio banco, não
  bate na API do IBGE a cada requisição do usuário.
- Consultas e filtros via API (`/api/v1/estados`, `/api/v1/municipios`
  com filtro por estado, região, busca por nome de município, ordenação e limite).
- Frontend com dashboard (Vue) — tabela ranking + gráfico de dispersão
  (renda × índice de envelhecimento, bolha = população), com os
  filtros acima atualizando as duas visualizações.
- Docker / Docker Compose — os 3 serviços sobem juntos com
  `docker compose up`.

**Extra (não pedido, entregue de qualquer forma):**
- Testes unitários (backend).
- `Makefile` com os comandos do dia a dia.
- `backend/ARQUITETURA.md` com o detalhamento técnico completo.
- Paginação no endpoint `/api/v1/municipios`.
- CI no GitHub Actions (`.github/workflows/ci.yml`): roda os testes
  automatizados do backend e confirma o build do frontend a cada
  push/PR pra `main`.



## Limitações conhecidas e próximos passos

- **Dado de referência é 2021/2022, não tempo real.** É limitação
  estrutural do IBGE (ver acima), não do projeto — mas significa que a
  aplicação não reflete a população/renda de hoje, e sim do último
  Censo/estimativa disponível.


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
- **Estrutura inicial e redação da análise do legado:** pedi para a IA
  montar o esqueleto de pastas/README; revisei o texto e
  ajustei antes de commitar.
- **Testes automatizados:** Utilizei IA para implementar seguindo uma
  política que eu já tinha decidido antes de qualquer teste existir
  (Postgres real num banco isolado, não SQLite — mesmo motivo do banco
  de desenvolvimento; teste obrigatório por funcionalidade). São testes
  de integração da API (batem no endpoint de verdade, banco real), não
  testes unitários no sentido estrito — decisão consciente pra pegar
  bug de verdade entre as camadas, não só validar uma função isolada.
- **Telas do frontend:** Solicitei à IA para implementar em cima de decisões
  que eu já tinha tomado (quais 2 visualizações mostrar, e o que cada
  uma responde de negócio — tabela ranking e dispersão renda × índice
  de envelhecimento). Testei no navegador de verdade antes de aceitar
  — inclusive encontrei um bug de CORS que a API não mostrava ao testar
  via terminal, só apareceu no navegador.

