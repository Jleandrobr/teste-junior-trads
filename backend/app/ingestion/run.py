import sys

from app.db.session import SessionLocal
from app.services.ingestao_service import (
    ingerir_beneficiarios,
    ingerir_empresa,
    ingerir_localidades,
    ingerir_perfil_demografico,
    ingerir_populacao,
    ingerir_renda,
)


def executar_etapa(db, nome: str, funcao) -> None:
    print(f"Ingerindo {nome}...")
    try:
        funcao(db)
    except Exception as erro:
        db.rollback()
        print(f"ERRO na etapa '{nome}': {type(erro).__name__}: {erro}")
        sys.exit(1)
    print(f"{nome}: ok.")


def main() -> None:
    db = SessionLocal()
    try:
        executar_etapa(db, "estados e municípios", ingerir_localidades)
        executar_etapa(db, "população (agregado 6579)", ingerir_populacao)
        executar_etapa(db, "perfil demográfico (agregado 9515)", ingerir_perfil_demografico)
        executar_etapa(db, "renda (agregados 10289 e 10295)", ingerir_renda)
        executar_etapa(db, "empresas (agregado 1685)", ingerir_empresa)
        executar_etapa(db, "beneficiários de plano médico (ANS)", ingerir_beneficiarios)
    finally:
        db.close()


if __name__ == "__main__":
    main()
