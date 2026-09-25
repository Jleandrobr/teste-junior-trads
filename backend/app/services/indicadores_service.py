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
    offset: int,
):
    return municipio_repository.listar_com_indicadores(
        db, estado, nome_municipio, regiao, ordenar_por, direcao, limite, offset
    )


def _destaque(linhas, campo: str) -> dict | None:
    if not linhas:
        return None
    melhor = max(linhas, key=lambda linha: getattr(linha, campo))
    return {"nome": melhor.nome, "estado": melhor.estado, "valor": float(getattr(melhor, campo))}


def _percentual(parte: int, todo: int) -> float:
    return parte * 100.0 / todo if todo else 0.0


def resumir_municipios(
    db: Session,
    estado: str | None,
    nome_municipio: str | None,
    regiao: str | None,
) -> dict:
    linhas = municipio_repository.resumir(db, estado, nome_municipio, regiao)

    populacao_total = sum(linha.populacao for linha in linhas)
    beneficiarios_medicos = sum(linha.qtd_beneficiarios_medicos for linha in linhas)
    beneficiarios_odonto = sum(linha.qtd_beneficiarios_odonto for linha in linhas)
    renda_ponderada = sum(float(linha.renda_per_capita_media) * linha.populacao for linha in linhas)

    return {
        "total_municipios": len(linhas),
        "populacao_total": populacao_total,
        "qtd_beneficiarios_medicos": beneficiarios_medicos,
        "qtd_beneficiarios_odonto": beneficiarios_odonto,
        "populacao_sem_plano_medico": populacao_total - beneficiarios_medicos,
        "populacao_sem_odonto": populacao_total - beneficiarios_odonto,
        "percentual_adesao_plano_medico": _percentual(beneficiarios_medicos, populacao_total),
        "percentual_adesao_odonto": _percentual(beneficiarios_odonto, populacao_total),
        "qtd_empresas": sum(linha.qtd_empresas for linha in linhas),
        "pessoal_assalariado": sum(linha.pessoal_assalariado for linha in linhas),
        "renda_per_capita_media_ponderada": renda_ponderada / populacao_total if populacao_total else 0.0,
        "destaques": {
            "maior_mercado_sem_plano_medico": _destaque(linhas, "populacao_sem_plano_medico"),
            "maior_mercado_sem_odonto": _destaque(linhas, "populacao_sem_odonto"),
            "maior_densidade_empresarial": _destaque(linhas, "empresas_por_mil_habitantes"),
            "maior_renda_per_capita": _destaque(linhas, "renda_per_capita_media"),
        },
    }
