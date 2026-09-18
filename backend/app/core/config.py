from pydantic_settings import BaseSettings


class Configuracoes(BaseSettings):
    database_url: str


configuracoes = Configuracoes()
