from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import MunicipiosPaginadosResponse, ResumoResponse
from app.services import indicadores_service

router = APIRouter(prefix="/api/v1/municipios", tags=["municipios"])

OrdenarPor = Literal[
    "populacao",
    "renda_media",
    "renda_mediana",
    "renda_per_capita_media",
    "renda_per_capita_mediana",
    "indice_envelhecimento",
    "beneficiarios",
    "adesao",
    "sem_plano",
    "beneficiarios_odonto",
    "adesao_odonto",
    "sem_odonto",
    "empresas",
    "empresas_por_mil",
    "assalariados_por_mil",
]
Regiao = Literal["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
Direcao = Literal["asc", "desc"]


@router.get("/resumo", response_model=ResumoResponse)
def resumir_municipios(
    estado: str | None = None,
    nome_municipio: str | None = None,
    regiao: Regiao | None = None,
    db: Session = Depends(get_db),
):
    return indicadores_service.resumir_municipios(db, estado, nome_municipio, regiao)


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
