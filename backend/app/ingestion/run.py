from app.db.session import SessionLocal
from app.services.ingestao_service import ingerir_localidades


def main() -> None:
    db = SessionLocal()
    try:
        print("Ingerindo estados e municípios...")
        ingerir_localidades(db) #  python -m app.ingestion.run
        print("Catálogo de localidades ingerido com sucesso.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
