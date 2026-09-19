from app.db.session import SessionLocal
from app.services.ingestao_service import ingerir_localidades, ingerir_populacao


def main() -> None:
    db = SessionLocal()
    try:
        print("Ingerindo estados e municípios...")
        ingerir_localidades(db) #  python -m app.ingestion.run
        print("Catálogo de localidades ingerido com sucesso.")

        print("Ingerindo população (agregado 6579)...")
        ingerir_populacao(db)
        print("População ingerida com sucesso.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
