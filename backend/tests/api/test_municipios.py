import pytest

from app.db.models import Beneficiario, Empresa, Estado, Municipio, PerfilDemografico, Populacao, Renda


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
    qtd_beneficiarios_medicos=None,
    qtd_beneficiarios_odonto=0,
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
    if qtd_beneficiarios_medicos is not None:
        db_session.add(
            Beneficiario(
                municipio_id=municipio_id,
                ano=2026,
                qtd_beneficiarios_medicos=qtd_beneficiarios_medicos,
                qtd_beneficiarios_odonto=qtd_beneficiarios_odonto,
            )
        )
    db_session.commit()


def test_listar_municipios_retorna_indicadores_combinados(client, db_session):
    criar_municipio_completo(db_session, 2507507, "João Pessoa", 25, "PB", populacao=800000)

    resposta = client.get("/api/v1/municipios")

    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["total"] == 1
    assert len(dados["resultados"]) == 1
    assert dados["resultados"][0]["nome"] == "João Pessoa"
    assert dados["resultados"][0]["estado"] == "PB"
    assert dados["resultados"][0]["populacao"] == 800000
    assert dados["resultados"][0]["qtd_beneficiarios_medicos"] == 0
    assert dados["resultados"][0]["percentual_adesao_plano_medico"] == 0.0
    assert dados["resultados"][0]["populacao_sem_plano_medico"] == 800000


def test_listar_municipios_filtra_por_estado(client, db_session):
    criar_municipio_completo(db_session, 2507507, "João Pessoa", 25, "PB")
    criar_municipio_completo(db_session, 3550308, "São Paulo", 35, "SP", regiao="Sudeste")

    resposta = client.get("/api/v1/municipios?estado=PB")

    dados = resposta.json()["resultados"]
    assert len(dados) == 1
    assert dados[0]["nome"] == "João Pessoa"


def test_listar_municipios_busca_por_nome_ignora_acento(client, db_session):
    criar_municipio_completo(db_session, 2507507, "João Pessoa", 25, "PB")

    resposta = client.get("/api/v1/municipios?nome_municipio=joao pessoa")

    dados = resposta.json()["resultados"]
    assert len(dados) == 1
    assert dados[0]["nome"] == "João Pessoa"


def test_listar_municipios_ordena_e_limita(client, db_session):
    criar_municipio_completo(db_session, 2507507, "João Pessoa", 25, "PB", populacao=800000)
    criar_municipio_completo(db_session, 3550308, "São Paulo", 35, "SP", regiao="Sudeste", populacao=12000000)
    criar_municipio_completo(db_session, 3106200, "Belo Horizonte", 31, "MG", regiao="Sudeste", populacao=2500000)

    resposta = client.get("/api/v1/municipios?ordenar_por=populacao&direcao=asc&limite=2")

    dados = resposta.json()
    assert dados["total"] == 3
    assert [linha["nome"] for linha in dados["resultados"]] == ["João Pessoa", "Belo Horizonte"]


def test_listar_municipios_pagina_com_offset(client, db_session):
    criar_municipio_completo(db_session, 2507507, "João Pessoa", 25, "PB", populacao=800000)
    criar_municipio_completo(db_session, 3550308, "São Paulo", 35, "SP", regiao="Sudeste", populacao=12000000)
    criar_municipio_completo(db_session, 3106200, "Belo Horizonte", 31, "MG", regiao="Sudeste", populacao=2500000)

    resposta = client.get("/api/v1/municipios?ordenar_por=populacao&direcao=asc&limite=2&offset=2")

    dados = resposta.json()
    assert dados["total"] == 3
    assert [linha["nome"] for linha in dados["resultados"]] == ["São Paulo"]


def test_listar_municipios_pagina_com_offset_na_busca_por_nome(client, db_session):
    criar_municipio_completo(db_session, 2507507, "João Pessoa", 25, "PB")
    criar_municipio_completo(db_session, 3550308, "São Paulo", 35, "SP", regiao="Sudeste")

    resposta = client.get("/api/v1/municipios?ordenar_por=populacao&direcao=asc&limite=1&offset=1")

    dados = resposta.json()
    assert dados["total"] == 2
    assert len(dados["resultados"]) == 1


def test_listar_municipios_nao_inclui_municipio_com_dado_incompleto(client, db_session):
    criar_municipio_completo(db_session, 2507507, "João Pessoa", 25, "PB")

    db_session.merge(Estado(id=51, sigla="MT", nome="Mato Grosso", regiao="Centro-Oeste"))
    db_session.merge(Municipio(id=5101837, nome="Boa Esperança do Norte", estado_id=51))
    db_session.commit()

    resposta = client.get("/api/v1/municipios")

    nomes = [linha["nome"] for linha in resposta.json()["resultados"]]
    assert "João Pessoa" in nomes
    assert "Boa Esperança do Norte" not in nomes


def test_listar_municipios_filtra_por_regiao(client, db_session):
    criar_municipio_completo(db_session, 2507507, "João Pessoa", 25, "PB")
    criar_municipio_completo(db_session, 3550308, "São Paulo", 35, "SP", regiao="Sudeste")

    resposta = client.get("/api/v1/municipios?regiao=Norte")

    dados = resposta.json()
    assert dados["total"] == 0
    assert len(dados["resultados"]) == 0

    resposta = client.get("/api/v1/municipios?regiao=Nordeste")

    dados = resposta.json()
    assert dados["total"] == 1
    assert dados["resultados"][0]["nome"] == "João Pessoa"


def test_listar_municipios_calcula_populacao_sem_plano_medico(client, db_session):
    criar_municipio_completo(
        db_session,
        2507507,
        "João Pessoa",
        25,
        "PB",
        populacao=800000,
        qtd_beneficiarios_medicos=280000,
        qtd_beneficiarios_odonto=384000,
    )

    resposta = client.get("/api/v1/municipios")

    municipio = resposta.json()["resultados"][0]
    assert municipio["qtd_beneficiarios_medicos"] == 280000
    assert municipio["populacao_sem_plano_medico"] == 520000
    assert municipio["percentual_adesao_plano_medico"] == 35.0


def test_listar_municipios_ordena_por_populacao_sem_plano(client, db_session):
    criar_municipio_completo(
        db_session, 2507507, "João Pessoa", 25, "PB",
        populacao=1000000, qtd_beneficiarios_medicos=900000,
    )
    criar_municipio_completo(
        db_session, 3106200, "Belo Horizonte", 31, "MG", regiao="Sudeste",
        populacao=500000, qtd_beneficiarios_medicos=50000,
    )
    criar_municipio_completo(
        db_session, 3550308, "São Paulo", 35, "SP", regiao="Sudeste",
        populacao=2000000, qtd_beneficiarios_medicos=1000000,
    )

    resposta = client.get("/api/v1/municipios?ordenar_por=sem_plano&direcao=desc")

    resultados = resposta.json()["resultados"]
    assert [linha["nome"] for linha in resultados] == ["São Paulo", "Belo Horizonte", "João Pessoa"]
    assert [linha["populacao_sem_plano_medico"] for linha in resultados] == [1000000, 450000, 100000]


@pytest.mark.parametrize("parametros", ["limite=0", "limite=-1", "limite=201", "offset=-1"])
def test_listar_municipios_rejeita_paginacao_invalida(client, parametros):
    resposta = client.get(f"/api/v1/municipios?{parametros}")

    assert resposta.status_code == 422


def test_listar_municipios_aceita_limite_maximo(client, db_session):
    criar_municipio_completo(db_session, 2507507, "João Pessoa", 25, "PB")

    resposta = client.get("/api/v1/municipios?limite=200&offset=0")

    assert resposta.status_code == 200
    assert resposta.json()["total"] == 1
