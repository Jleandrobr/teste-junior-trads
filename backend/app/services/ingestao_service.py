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

AGREGADO_RENDA = 10289
VARIAVEL_RENDIMENTO_MEDIO = 13536
VARIAVEL_RENDIMENTO_MEDIANO = 13537
ANO_RENDA = 2022
CLASSIFICACAO_RENDA = "2[6794]|86[95251]"

AGREGADO_EMPRESA = 1685
VARIAVEL_QTD_EMPRESAS = 367
VARIAVEL_PESSOAL_ASSALARIADO = 708
VARIAVEL_SALARIOS = 662
ANO_EMPRESA = 2021


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


def ingerir_renda(db: Session) -> None:
    ano = ANO_RENDA

    serie_medio = buscar_serie(AGREGADO_RENDA, ano, VARIAVEL_RENDIMENTO_MEDIO, CLASSIFICACAO_RENDA)
    medio = extrair_valores(serie_medio, ano)

    serie_mediano = buscar_serie(AGREGADO_RENDA, ano, VARIAVEL_RENDIMENTO_MEDIANO, CLASSIFICACAO_RENDA)
    mediano = extrair_valores(serie_mediano, ano)

    for municipio_id in medio:
        if municipio_id not in mediano:
            print(f"aviso: município {municipio_id} sem renda completa - pulando")
            continue

        indicador_repository.salvar_renda(
            db,
            municipio_id,
            ano,
            medio[municipio_id],
            mediano[municipio_id],
        )
    db.commit()


def ingerir_empresa(db: Session) -> None:
    ano = ANO_EMPRESA

    serie_qtd = buscar_serie(AGREGADO_EMPRESA, ano, VARIAVEL_QTD_EMPRESAS)
    qtd = extrair_valores(serie_qtd, ano)

    serie_pessoal = buscar_serie(AGREGADO_EMPRESA, ano, VARIAVEL_PESSOAL_ASSALARIADO)
    pessoal = extrair_valores(serie_pessoal, ano)

    serie_salarios = buscar_serie(AGREGADO_EMPRESA, ano, VARIAVEL_SALARIOS)
    salarios = extrair_valores(serie_salarios, ano)

    for municipio_id in qtd:
        if municipio_id not in pessoal or municipio_id not in salarios:
            print(f"aviso: município {municipio_id} sem dados de empresas completos - pulando")
            continue

        indicador_repository.salvar_empresa(
            db,
            municipio_id,
            ano,
            int(qtd[municipio_id]),
            int(pessoal[municipio_id]),
            salarios[municipio_id],
        )
    db.commit()
