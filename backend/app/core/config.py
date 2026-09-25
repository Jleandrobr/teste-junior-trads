from pydantic_settings import BaseSettings


class Configuracoes(BaseSettings):
    database_url: str
    ingestao_cron: str = "0 3 1 * *"


configuracoes = Configuracoes()
