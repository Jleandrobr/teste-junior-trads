from app.db.models import Estado


def test_listar_estados_retorna_ordenado_por_nome(client, db_session):
    db_session.add(Estado(id=25, sigla="PB", nome="Paraíba", regiao="Nordeste"))
    db_session.add(Estado(id=11, sigla="RO", nome="Rondônia", regiao="Norte"))
    db_session.commit()

    resposta = client.get("/api/v1/estados")

    assert resposta.status_code == 200
    nomes = [estado["nome"] for estado in resposta.json()]
    assert nomes == ["Paraíba", "Rondônia"]


def test_listar_estados_vazio_quando_sem_dados(client):
    resposta = client.get("/api/v1/estados")

    assert resposta.status_code == 200
    assert resposta.json() == []
