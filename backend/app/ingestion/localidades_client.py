import requests

from app.ingestion.schemas import EstadoIBGE, MunicipioIBGE

BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades"


def buscar_estados() -> list[EstadoIBGE]:
    resposta = requests.get(f"{BASE_URL}/estados", timeout=30)
    resposta.raise_for_status()
    return [EstadoIBGE.model_validate(item) for item in resposta.json()]


def buscar_municipios() -> list[MunicipioIBGE]:
    resposta = requests.get(f"{BASE_URL}/municipios", timeout=30)
    resposta.raise_for_status()
    return [MunicipioIBGE.model_validate(item) for item in resposta.json()]
