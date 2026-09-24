from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import MunicipiosPaginadosResponse
from app.services import indicadores_service

router = APIRouter(prefix="/api/v1/municipios", tags=["municipios"])

OrdenarPor = Literal[
    "populacao",
    "renda_media",
    "renda_mediana",
    "indice_envelhecimento",
    "beneficiarios",
    "adesao",
    "sem_plano",
]
Regiao = Literal["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
Direcao = Literal["asc", "desc"]


@router.get("", response_model=MunicipiosPaginadosResponse)
def listar_municipios(
    estado: str | None = None,
    nome_municipio: str | None = None,
    regiao: Regiao | None = None,
    ordenar_por: OrdenarPor = "populacao",
    direcao: Direcao = "desc",
    limite: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    total, resultados = indicadores_service.listar_municipios(
        db, estado, nome_municipio, regiao, ordenar_por, direcao, limite, offset
    )
    return {"total": total, "resultados": resultados}
