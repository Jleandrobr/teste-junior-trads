from sqlalchemy.orm import Session

from app.ingestion.ibge_client import buscar_serie, extrair_valores
from app.ingestion.localidades_client import buscar_estados, buscar_municipios
from app.repositories import estado_repository, indicador_repository, municipio_repository

AGREGADO_POPULACAO = 6579
VARIAVEL_POPULACAO = 9324
ANO_POPULACAO = 2021


def ingerir_localidades(db: Session) -> None:
    estados = buscar_estados()
    for estado in estados:
        estado_repository.salvar(db, estado.id, estado.sigla, estado.nome, estado.regiao.nome)
    db.commit()

    municipios = buscar_municipios()
    for municipio in municipios:
        municipio_repository.salvar(db, municipio.id, municipio.nome, municipio.estado_id)
    db.commit()


def ingerir_populacao(db: Session) -> None:
    series = buscar_serie(AGREGADO_POPULACAO, ANO_POPULACAO, VARIAVEL_POPULACAO)
    valores = extrair_valores(series, ANO_POPULACAO)
    for municipio_id, valor in valores.items():
        indicador_repository.salvar_populacao(db, municipio_id, ANO_POPULACAO, int(valor))
    db.commit()
