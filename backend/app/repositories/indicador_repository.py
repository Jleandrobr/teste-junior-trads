from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.models import Empresa, PerfilDemografico, Populacao, Renda


def salvar_populacao(db: Session, municipio_id: int, ano: int, populacao: int) -> None:
    stmt = insert(Populacao).values(municipio_id=municipio_id, ano=ano, populacao=populacao)
    stmt = stmt.on_conflict_do_update(
        index_elements=["municipio_id", "ano"],
        set_={"populacao": populacao},
    )
    db.execute(stmt)


def salvar_perfil_demografico(
    db: Session,
    municipio_id: int,
    ano: int,
    indice_envelhecimento: float,
    idade_mediana: float,
    razao_sexo: float,
) -> None:
    valores = {
        "indice_envelhecimento": indice_envelhecimento,
        "idade_mediana": idade_mediana,
        "razao_sexo": razao_sexo,
    }
    stmt = insert(PerfilDemografico).values(municipio_id=municipio_id, ano=ano, **valores)
    stmt = stmt.on_conflict_do_update(index_elements=["municipio_id", "ano"], set_=valores)
    db.execute(stmt)


def salvar_renda(
    db: Session,
    municipio_id: int,
    ano: int,
    rendimento_medio: float,
    rendimento_mediano: float,
) -> None:
    stmt = insert(Renda).values(
        municipio_id=municipio_id,
        ano=ano,
        rendimento_medio=rendimento_medio,
        rendimento_mediano=rendimento_mediano,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["municipio_id", "ano"],
        set_={
            "rendimento_medio": rendimento_medio,
            "rendimento_mediano": rendimento_mediano,
        },
    )
    db.execute(stmt)


def salvar_empresa(
    db: Session,
    municipio_id: int,
    ano: int,
    qtd_empresas: int,
    pessoal_assalariado: int,
    salarios_mil_reais: float,
) -> None:
    stmt = insert(Empresa).values(
        municipio_id=municipio_id,
        ano=ano,
        qtd_empresas=qtd_empresas,
        pessoal_assalariado=pessoal_assalariado,
        salarios_mil_reais=salarios_mil_reais,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["municipio_id", "ano"],
        set_={
            "qtd_empresas": qtd_empresas,
            "pessoal_assalariado": pessoal_assalariado,
            "salarios_mil_reais": salarios_mil_reais,
        },
    )
    db.execute(stmt)
