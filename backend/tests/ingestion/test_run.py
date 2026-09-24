from unittest.mock import MagicMock

import pytest

from app.ingestion.run import executar_etapa


def test_executar_etapa_imprime_ok_quando_funciona(capsys):
    db = MagicMock()
    funcao = MagicMock()

    executar_etapa(db, "renda", funcao)

    funcao.assert_called_once_with(db)
    assert "renda: ok." in capsys.readouterr().out


def test_executar_etapa_mostra_qual_etapa_falhou_e_sai_com_codigo_1(capsys):
    db = MagicMock()

    def funcao_que_falha(_db):
        raise ValueError("IBGE não retornou dados")

    with pytest.raises(SystemExit) as saida:
        executar_etapa(db, "população (agregado 6579)", funcao_que_falha)

    assert saida.value.code == 1
    db.rollback.assert_called_once()
    mensagem = capsys.readouterr().out
    assert "ERRO na etapa 'população (agregado 6579)'" in mensagem
    assert "ValueError: IBGE não retornou dados" in mensagem
