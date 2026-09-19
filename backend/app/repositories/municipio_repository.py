from sqlalchemy.orm import Session

from app.db.models import Municipio


def salvar(db: Session, codigo_ibge: int, nome: str, estado_id: int) -> None:
    db.merge(Municipio(id=codigo_ibge, nome=nome, estado_id=estado_id))
