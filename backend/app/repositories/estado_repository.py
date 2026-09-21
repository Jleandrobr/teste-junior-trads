from sqlalchemy.orm import Session

from app.db.models import Estado


def salvar(db: Session, codigo_ibge: int, sigla: str, nome: str, regiao: str) -> None:
    db.merge(Estado(id=codigo_ibge, sigla=sigla, nome=nome, regiao=regiao))


def listar(db: Session) -> list[Estado]:
    return db.query(Estado).order_by(Estado.nome).all()
