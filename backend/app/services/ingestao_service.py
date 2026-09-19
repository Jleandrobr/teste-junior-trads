from sqlalchemy.orm import Session

from app.ingestion.localidades_client import buscar_estados, buscar_municipios
from app.repositories import estado_repository, municipio_repository


def ingerir_localidades(db: Session) -> None:
    estados = buscar_estados()
    for estado in estados:
        estado_repository.salvar(db, estado.id, estado.sigla, estado.nome, estado.regiao.nome)
    db.commit()

    municipios = buscar_municipios()
    for municipio in municipios:
        municipio_repository.salvar(db, municipio.id, municipio.nome, municipio.estado_id)
    db.commit()
