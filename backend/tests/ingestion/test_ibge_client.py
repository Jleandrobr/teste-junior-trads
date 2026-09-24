from unittest.mock import MagicMock, patch

import pytest

from app.ingestion.ibge_client import buscar_serie


def resposta_falsa(json_retornado):
    resposta = MagicMock()
    resposta.json.return_value = json_retornado
    return resposta


def test_buscar_serie_retorna_as_series_da_resposta():
    json_do_ibge = [{"resultados": [{"series": [{"localidade": {"id": "2507507"}, "serie": {"2021": "825796"}}]}]}]

    with patch("app.ingestion.ibge_client.requests.get", return_value=resposta_falsa(json_do_ibge)):
        series = buscar_serie(6579, 2021, 9324)

    assert series[0]["localidade"]["id"] == "2507507"


def test_buscar_serie_da_erro_claro_quando_ibge_devolve_lista_vazia():
    with patch("app.ingestion.ibge_client.requests.get", return_value=resposta_falsa([])):
        with pytest.raises(ValueError) as erro:
            buscar_serie(9515, 2030, 10612)

    assert "agregado 9515" in str(erro.value)
    assert "ano 2030" in str(erro.value)


def test_buscar_serie_da_erro_claro_quando_resposta_nao_tem_resultados():
    with patch("app.ingestion.ibge_client.requests.get", return_value=resposta_falsa([{"resultados": []}])):
        with pytest.raises(ValueError):
            buscar_serie(1685, 2021, 367)
