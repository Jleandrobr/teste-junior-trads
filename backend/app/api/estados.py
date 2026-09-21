from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import EstadoResponse
from app.services import indicadores_service

router = APIRouter(prefix="/api/v1/estados", tags=["estados"])


@router.get("", response_model=list[EstadoResponse])
def listar_estados(db: Session = Depends(get_db)):
    return indicadores_service.listar_estados(db)
