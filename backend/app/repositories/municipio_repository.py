import unicodedata

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Beneficiario, Empresa, Estado, Municipio, PerfilDemografico, Populacao, Renda

QTD_BENEFICIARIOS_MEDICOS = func.coalesce(Beneficiario.qtd_beneficiarios_medicos, 0)
PERCENTUAL_ADESAO_PLANO_MEDICO = QTD_BENEFICIARIOS_MEDICOS * 100.0 / Populacao.populacao
POPULACAO_SEM_PLANO_MEDICO = Populacao.populacao - QTD_BENEFICIARIOS_MEDICOS

COLUNAS_ORDENAVEIS = {
    "populacao": Populacao.populacao,
    "renda_media": Renda.rendimento_medio,
    "renda_mediana": Renda.rendimento_mediano,
    "indice_envelhecimento": PerfilDemografico.indice_envelhecimento,
    "beneficiarios": QTD_BENEFICIARIOS_MEDICOS,
    "adesao": PERCENTUAL_ADESAO_PLANO_MEDICO,
    "sem_plano": POPULACAO_SEM_PLANO_MEDICO,
}


def remover_acentos(texto: str) -> str:
    forma_decomposta = unicodedata.normalize("NFKD", texto)
    return "".join(letra for letra in forma_decomposta if not unicodedata.combining(letra))


def salvar(db: Session, codigo_ibge: int, nome: str, estado_id: int) -> None:
    db.merge(Municipio(id=codigo_ibge, nome=nome, estado_id=estado_id))


def listar_com_indicadores(
    db: Session,
    estado: str | None,
    nome_municipio: str | None,
    regiao: str | None,
    ordenar_por: str,
    direcao: str,
    limite: int,
    offset: int,
):
    query = (
        select(
            Municipio.id,
            Municipio.nome,
            Estado.sigla.label("estado"),
            Populacao.populacao,
            PerfilDemografico.indice_envelhecimento,
            PerfilDemografico.idade_mediana,
            Renda.rendimento_medio.label("renda_media"),
            Renda.rendimento_mediano.label("renda_mediana"),
            Empresa.qtd_empresas,
            QTD_BENEFICIARIOS_MEDICOS.label("qtd_beneficiarios_medicos"),
            PERCENTUAL_ADESAO_PLANO_MEDICO.label("percentual_adesao_plano_medico"),
            POPULACAO_SEM_PLANO_MEDICO.label("populacao_sem_plano_medico"),
        )
        .join(Estado, Estado.id == Municipio.estado_id)
        .join(Populacao, Populacao.municipio_id == Municipio.id)
        .join(PerfilDemografico, PerfilDemografico.municipio_id == Municipio.id)
        .join(Renda, Renda.municipio_id == Municipio.id)
        .join(Empresa, Empresa.municipio_id == Municipio.id)
        .outerjoin(Beneficiario, Beneficiario.municipio_id == Municipio.id)
    )

    if estado is not None:
        query = query.where(Estado.sigla == estado)

    if regiao is not None:
        query = query.where(Estado.regiao == regiao)

    coluna_ordenacao = COLUNAS_ORDENAVEIS[ordenar_por]
    if direcao == "asc":
        query = query.order_by(coluna_ordenacao.asc())
    else:
        query = query.order_by(coluna_ordenacao.desc())

    resultado = db.execute(query).all()

    if nome_municipio is not None:
        busca_normalizada = remover_acentos(nome_municipio).lower()
        resultado = [
            linha
            for linha in resultado
            if busca_normalizada in remover_acentos(linha.nome).lower()
        ]

    total = len(resultado)
    resultado_pagina = resultado[offset : offset + limite]
    return total, resultado_pagina
