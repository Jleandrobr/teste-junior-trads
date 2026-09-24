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
    qtd_beneficiarios_medicos: int
    percentual_adesao_plano_medico: float
    populacao_sem_plano_medico: int

    model_config = {"from_attributes": True}


class MunicipiosPaginadosResponse(BaseModel):
    total: int
    resultados: list[MunicipioComIndicadoresResponse]
