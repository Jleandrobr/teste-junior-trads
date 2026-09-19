from sqlalchemy.orm import Session

from app.db.models import Estado


def salvar(db: Session, codigo_ibge: int, sigla: str, nome: str, regiao: str) -> None:
    db.merge(Estado(id=codigo_ibge, sigla=sigla, nome=nome, regiao=regiao))
