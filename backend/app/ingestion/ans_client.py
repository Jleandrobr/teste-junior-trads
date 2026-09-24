import csv
import io

import requests

URL_TAXA_COBERTURA = (
    "https://dadosabertos.ans.gov.br/FTP/PDA/taxa_de_cobertura_de_planos_de_saude-047/"
    "pda-047-taxa_cobertura.csv"
)


def baixar_beneficiarios(ano: int) -> tuple[dict[int, int], dict[int, int]]:
    resposta = requests.get(URL_TAXA_COBERTURA, timeout=120)
    resposta.raise_for_status()

    texto = resposta.content.decode("latin-1")
    leitor = csv.DictReader(io.StringIO(texto), delimiter=";")

    medicos_por_municipio: dict[int, int] = {}
    odonto_por_municipio: dict[int, int] = {}
    linhas_de_outro_periodo = 0
    for linha in leitor:
        if linha["PERIODO"] != str(ano):
            linhas_de_outro_periodo += 1
            continue
        try:
            cd_municipio = int(linha["CD_MUNICIPIO"])
            medicos = int(linha["BENEF_ASSISTENCIA_MEDICA"])
            odonto = int(linha["BENEF_EXCLUS_ODONTOLOGICO"])
        except (ValueError, KeyError):
            print(f"aviso: linha inválida no CSV da ANS - pulando ({linha!r})")
            continue
        medicos_por_municipio[cd_municipio] = medicos_por_municipio.get(cd_municipio, 0) + medicos
        odonto_por_municipio[cd_municipio] = odonto_por_municipio.get(cd_municipio, 0) + odonto

    if linhas_de_outro_periodo > 0:
        print(f"aviso: {linhas_de_outro_periodo} linhas do CSV da ANS não são de {ano} - ignoradas")

    if not medicos_por_municipio:
        raise ValueError(f"O CSV da ANS não tem nenhuma linha válida do ano {ano} - confira ANO_BENEFICIARIOS")

    return medicos_por_municipio, odonto_por_municipio
