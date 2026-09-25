import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import configuracoes
from app.ingestion.run import main as executar_ingestao

logger = logging.getLogger("agendador")


def rodar_ingestao() -> None:
    try:
        executar_ingestao()
    except SystemExit:
        logger.error("Ingestão falhou - nova tentativa no próximo agendamento")
    except Exception:
        logger.exception("Erro inesperado na ingestão - nova tentativa no próximo agendamento")


def criar_agendador(expressao_cron: str) -> BlockingScheduler:
    agendador = BlockingScheduler()
    agendador.add_job(
        rodar_ingestao,
        CronTrigger.from_crontab(expressao_cron),
        id="ingestao",
        max_instances=1,
        coalesce=True,
    )
    return agendador


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    agendador = criar_agendador(configuracoes.ingestao_cron)
    logger.info("Agendador iniciado (cron: %s)", configuracoes.ingestao_cron)
    agendador.start()


if __name__ == "__main__":
    main()
