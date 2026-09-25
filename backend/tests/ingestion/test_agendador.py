from unittest.mock import MagicMock

import pytest

from app.ingestion import agendador


def test_criar_agendador_registra_um_job_com_o_cron_informado():
    sched = agendador.criar_agendador("0 3 1 * *")

    job = sched.get_job("ingestao")

    assert job is not None
    assert job.max_instances == 1
    campos = {campo.name: str(campo) for campo in job.trigger.fields}
    assert campos["hour"] == "3"
    assert campos["day"] == "1"


def test_criar_agendador_rejeita_cron_invalido():
    with pytest.raises(ValueError):
        agendador.criar_agendador("isso não é um cron")


def test_rodar_ingestao_chama_a_ingestao(monkeypatch):
    executar = MagicMock()
    monkeypatch.setattr(agendador, "executar_ingestao", executar)

    agendador.rodar_ingestao()

    executar.assert_called_once_with()


def test_rodar_ingestao_nao_derruba_o_agendador_quando_a_ingestao_falha(monkeypatch):
    monkeypatch.setattr(agendador, "executar_ingestao", MagicMock(side_effect=SystemExit(1)))

    agendador.rodar_ingestao()
