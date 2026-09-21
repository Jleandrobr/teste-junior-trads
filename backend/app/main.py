from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import estados, municipios
from app.db.session import get_db

app = FastAPI(title="Painel de Inteligência de Mercado - Trads")
app.include_router(estados.router)
app.include_router(municipios.router)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
