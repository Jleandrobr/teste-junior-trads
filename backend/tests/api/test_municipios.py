from app.db.models import Empresa, Estado, Municipio, PerfilDemografico, Populacao, Renda


def criar_municipio_completo(
    db_session,
    municipio_id,
    nome,
    estado_id,
    estado_sigla,
    regiao="Nordeste",
    populacao=100000,
    indice_envelhecimento=50.0,
    renda_media=2000.0,
    renda_mediana=1500.0,
    qtd_empresas=100,
):
    db_session.merge(
        Estado(id=estado_id, sigla=estado_sigla, nome=f"Estado {estado_sigla}", regiao=regiao)
    )
    db_session.merge(Municipio(id=municipio_id, nome=nome, estado_id=estado_id))

    db_session.flush()

    db_session.add(Populacao(municipio_id=municipio_id, ano=2021, populacao=populacao))
    db_session.add(
        PerfilDemografico(
            municipio_id=municipio_id,
            ano=2022,
            indice_envelhecimento=indice_envelhecimento,
            idade_mediana=35.0,
            razao_sexo=90.0,
        )
    )
    db_session.add(
        Renda(
            municipio_id=municipio_id,
            ano=2022,
            rendimento_medio=renda_media,
            rendimento_mediano=renda_mediana,
        )
    )
    db_session.add(
        Empresa(
            municipio_id=municipio_id,
            ano=2021,
            qtd_empresas=qtd_empresas,
            pessoal_assalariado=1000,
            salarios_mil_reais=5000.0,
        )
    )
    db_session.commit()


def test_listar_municipios_retorna_indicadores_combinados(client, db_session):
    criar_municipio_completo(db_session, 2507507, "João Pessoa", 25, "PB", populacao=800000)

    resposta = client.get("/api/v1/municipios")

    assert resposta.status_code == 200
    dados = resposta.json()
    assert len(dados) == 1
    assert dados[0]["nome"] == "João Pessoa"
    assert dados[0]["estado"] == "PB"
    assert dados[0]["populacao"] == 800000


def test_listar_municipios_filtra_por_estado(client, db_session):
    criar_municipio_completo(db_session, 2507507, "João Pessoa", 25, "PB")
    criar_municipio_completo(db_session, 3550308, "São Paulo", 35, "SP", regiao="Sudeste")

    resposta = client.get("/api/v1/municipios?estado=PB")

    dados = resposta.json()
    assert len(dados) == 1
    assert dados[0]["nome"] == "João Pessoa"


def test_listar_municipios_busca_por_nome_ignora_acento(client, db_session):
    criar_municipio_completo(db_session, 2507507, "João Pessoa", 25, "PB")

    resposta = client.get("/api/v1/municipios?nome_municipio=joao pessoa")

    dados = resposta.json()
    assert len(dados) == 1
    assert dados[0]["nome"] == "João Pessoa"


def test_listar_municipios_ordena_e_limita(client, db_session):
    criar_municipio_completo(db_session, 2507507, "João Pessoa", 25, "PB", populacao=800000)
    criar_municipio_completo(db_session, 3550308, "São Paulo", 35, "SP", regiao="Sudeste", populacao=12000000)
    criar_municipio_completo(db_session, 3106200, "Belo Horizonte", 31, "MG", regiao="Sudeste", populacao=2500000)

    resposta = client.get("/api/v1/municipios?ordenar_por=populacao&direcao=asc&limite=2")

    dados = resposta.json()
    assert [linha["nome"] for linha in dados] == ["João Pessoa", "Belo Horizonte"]


def test_listar_municipios_nao_inclui_municipio_com_dado_incompleto(client, db_session):
    criar_municipio_completo(db_session, 2507507, "João Pessoa", 25, "PB")

    db_session.merge(Estado(id=51, sigla="MT", nome="Mato Grosso", regiao="Centro-Oeste"))
    db_session.merge(Municipio(id=5101837, nome="Boa Esperança do Norte", estado_id=51))
    db_session.commit()

    resposta = client.get("/api/v1/municipios")

    nomes = [linha["nome"] for linha in resposta.json()]
    assert "João Pessoa" in nomes
    assert "Boa Esperança do Norte" not in nomes


def test_listar_municipios_filtra_por_regiao(client, db_session):
    criar_municipio_completo(db_session, 2507507, "João Pessoa", 25, "PB")
    criar_municipio_completo(db_session, 3550308, "São Paulo", 35, "SP", regiao="Sudeste")

    resposta = client.get("/api/v1/municipios?regiao=Norte")

    dados = resposta.json()
    assert len(dados) == 0

    resposta = client.get("/api/v1/municipios?regiao=Nordeste")

    dados = resposta.json()
    assert len(dados) == 1
    assert dados[0]["nome"] == "João Pessoa"
