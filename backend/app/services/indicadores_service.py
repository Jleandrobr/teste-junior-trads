from sqlalchemy.orm import Session

from app.db.models import Estado
from app.repositories import estado_repository, municipio_repository


def listar_estados(db: Session) -> list[Estado]:
    return estado_repository.listar(db)


def listar_municipios(
    db: Session,
    estado: str | None,
    nome_municipio: str | None,
    regiao: str | None,
    ordenar_por: str,
    direcao: str,
    limite: int,
):
    return municipio_repository.listar_com_indicadores(db, estado, nome_municipio, regiao, ordenar_por, direcao, limite)
