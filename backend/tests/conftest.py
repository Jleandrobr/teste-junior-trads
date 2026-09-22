import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base, get_db
from app.main import app

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine):
    SessionLocalTeste = sessionmaker(bind=engine)
    session = SessionLocalTeste()
    yield session
    session.close()

    with engine.connect() as conexao:
        for tabela in reversed(Base.metadata.sorted_tables):
            conexao.execute(tabela.delete())
        conexao.commit()


@pytest.fixture
def client(db_session):
    def sobrescrever_get_db():
        yield db_session

    app.dependency_overrides[get_db] = sobrescrever_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
