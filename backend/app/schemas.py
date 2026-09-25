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
    renda_per_capita_media: float
    renda_per_capita_mediana: float
    qtd_empresas: int
    qtd_beneficiarios_medicos: int
    percentual_adesao_plano_medico: float
    populacao_sem_plano_medico: int
    qtd_beneficiarios_odonto: int
    percentual_adesao_odonto: float
    populacao_sem_odonto: int
    pessoal_assalariado: int
    empresas_por_mil_habitantes: float
    assalariados_por_mil_habitantes: float

    model_config = {"from_attributes": True}


class MunicipiosPaginadosResponse(BaseModel):
    total: int
    resultados: list[MunicipioComIndicadoresResponse]


class DestaqueResponse(BaseModel):
    nome: str
    estado: str
    valor: float


class DestaquesResponse(BaseModel):
    maior_mercado_sem_plano_medico: DestaqueResponse | None
    maior_mercado_sem_odonto: DestaqueResponse | None
    maior_densidade_empresarial: DestaqueResponse | None
    maior_renda_per_capita: DestaqueResponse | None


class ResumoResponse(BaseModel):
    total_municipios: int
    populacao_total: int
    qtd_beneficiarios_medicos: int
    qtd_beneficiarios_odonto: int
    populacao_sem_plano_medico: int
    populacao_sem_odonto: int
    percentual_adesao_plano_medico: float
    percentual_adesao_odonto: float
    qtd_empresas: int
    pessoal_assalariado: int
    renda_per_capita_media_ponderada: float
    destaques: DestaquesResponse
