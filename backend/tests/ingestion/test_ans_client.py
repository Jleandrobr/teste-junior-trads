from unittest.mock import MagicMock, patch

import pytest

from app.ingestion.ans_client import baixar_beneficiarios

CABECALHO = "PERIODO;CD_MUNICIPIO;NM_MUNICIPIO;BENEF_ASSISTENCIA_MEDICA;BENEF_EXCLUS_ODONTOLOGICO"


def resposta_com_csv(linhas):
    texto = "\n".join([CABECALHO] + linhas)
    resposta = MagicMock()
    resposta.content = texto.encode("latin-1")
    return resposta


def test_baixar_beneficiarios_soma_por_municipio_e_ignora_outro_ano():
    csv = resposta_com_csv(
        [
            '"2026";"250750";"Joao Pessoa";"10";"4"',
            '"2026";"250750";"Joao Pessoa";"5";"1"',
            '"2026";"140010";"Boa Vista";"7";"0"',
            '"2025";"140010";"Boa Vista";"99";"99"',
        ]
    )

    with patch("app.ingestion.ans_client.requests.get", return_value=csv):
        medicos, odonto = baixar_beneficiarios(2026)

    assert medicos == {250750: 15, 140010: 7}
    assert odonto == {250750: 5, 140010: 0}


def test_baixar_beneficiarios_pula_linha_invalida():
    csv = resposta_com_csv(
        [
            '"2026";"abc";"Cidade Quebrada";"10";"4"',
            '"2026";"250750";"Joao Pessoa";"3";"1"',
        ]
    )

    with patch("app.ingestion.ans_client.requests.get", return_value=csv):
        medicos, odonto = baixar_beneficiarios(2026)

    assert medicos == {250750: 3}
    assert odonto == {250750: 1}


def test_baixar_beneficiarios_da_erro_quando_csv_nao_tem_o_ano_esperado():
    csv = resposta_com_csv(['"2025";"250750";"Joao Pessoa";"10";"4"'])

    with patch("app.ingestion.ans_client.requests.get", return_value=csv):
        with pytest.raises(ValueError) as erro:
            baixar_beneficiarios(2026)

    assert "2026" in str(erro.value)
