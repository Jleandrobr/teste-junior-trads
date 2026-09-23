from pydantic import BaseModel


class EstadoResponse(BaseModel):
    id: int
    sigla: str
    nome: str
    regiao: str

    model_config = {"from_attributes": True}


class MunicipioComIndicadoresResponse(BaseModel):
    id: int
    nome: str
    estado: str
    populacao: int
    indice_envelhecimento: float
    idade_mediana: float
    renda_media: float
    renda_mediana: float
    qtd_empresas: int

    model_config = {"from_attributes": True}


class MunicipiosPaginadosResponse(BaseModel):
    total: int
    resultados: list[MunicipioComIndicadoresResponse]
