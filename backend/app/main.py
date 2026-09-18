from fastapi import FastAPI
from sqlalchemy import create_engine, text

from app.core.config import configuracoes

app = FastAPI(title="Painel de Inteligência de Mercado - Trads")
engine = create_engine(configuracoes.database_url)


@app.get("/health")
def health():
    with engine.connect() as conexao:
        conexao.execute(text("SELECT 1"))
    return {"status": "ok"}
