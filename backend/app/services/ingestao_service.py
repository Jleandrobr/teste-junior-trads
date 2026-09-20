from sqlalchemy.orm import Session

from app.ingestion.ibge_client import buscar_serie, extrair_valores
from app.ingestion.localidades_client import buscar_estados, buscar_municipios
from app.repositories import estado_repository, indicador_repository, municipio_repository

AGREGADO_POPULACAO = 6579
VARIAVEL_POPULACAO = 9324
ANO_POPULACAO = 2021

AGREGADO_PERFIL_DEMOGRAFICO = 9515
VARIAVEL_INDICE_ENVELHECIMENTO = 10612
VARIAVEL_IDADE_MEDIANA = 10613
VARIAVEL_RAZAO_SEXO = 8845
ANO_PERFIL_DEMOGRAFICO = 2022


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


def ingerir_perfil_demografico(db: Session) -> None:
    ano = ANO_PERFIL_DEMOGRAFICO

    serie_indice = buscar_serie(AGREGADO_PERFIL_DEMOGRAFICO, ano, VARIAVEL_INDICE_ENVELHECIMENTO)
    indice = extrair_valores(serie_indice, ano)

    serie_idade = buscar_serie(AGREGADO_PERFIL_DEMOGRAFICO, ano, VARIAVEL_IDADE_MEDIANA)
    idade = extrair_valores(serie_idade, ano)

    serie_razao = buscar_serie(AGREGADO_PERFIL_DEMOGRAFICO, ano, VARIAVEL_RAZAO_SEXO)
    razao = extrair_valores(serie_razao, ano)

    for municipio_id in indice:
        if municipio_id not in idade or municipio_id not in razao:
            print(f"aviso: município {municipio_id} sem perfil demográfico completo - pulando")
            continue

        indicador_repository.salvar_perfil_demografico(
            db,
            municipio_id,
            ano,
            indice[municipio_id],
            idade[municipio_id],
            razao[municipio_id],
        )
    db.commit()
