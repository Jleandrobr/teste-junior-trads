from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.models import Populacao


def salvar_populacao(db: Session, municipio_id: int, ano: int, populacao: int) -> None:
    stmt = insert(Populacao).values(municipio_id=municipio_id, ano=ano, populacao=populacao)
    stmt = stmt.on_conflict_do_update(
        index_elements=["municipio_id", "ano"],
        set_={"populacao": populacao},
    )
    db.execute(stmt)
