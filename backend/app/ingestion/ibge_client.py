import requests

BASE_URL = "https://servicodados.ibge.gov.br/api/v3/agregados"


def buscar_serie(agregado: int, ano: int, variavel: int, classificacao: str | None = None) -> list[dict]:
    url = f"{BASE_URL}/{agregado}/periodos/{ano}/variaveis/{variavel}?localidades=N6"
    if classificacao:
        url += f"&classificacao={classificacao}"
    resposta = requests.get(url, timeout=60)
    resposta.raise_for_status()
    dados = resposta.json()
    return dados[0]["resultados"][0]["series"]


def extrair_valores(series: list[dict], ano: int) -> dict[int, float]:
    valores: dict[int, float] = {}
    for item in series:
        municipio_id = int(item["localidade"]["id"])
        bruto = item["serie"][str(ano)]
        try:
            valores[municipio_id] = float(bruto)
        except ValueError:
            print(f"aviso: município {municipio_id} sem dado disponível ({bruto!r}) - pulando")
    return valores
