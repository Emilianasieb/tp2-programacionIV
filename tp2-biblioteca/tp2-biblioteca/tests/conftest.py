"""Fixtures compartidas: cada test usa una base SQLite en memoria nueva."""
import os

# Antes de importar la app: así el arranque de la app no crea un .db real en disco
os.environ["DATABASE_URL"] = "sqlite://"

import pytest  # noqa: E402
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app import models  # noqa: F401  (registra las tablas)
from app.database import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture():
    # StaticPool hace que todas las conexiones compartan la misma base en memoria
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    # Reemplazamos la dependencia real por la sesión de test
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


# ---- helpers para crear datos rápido ----

@pytest.fixture
def crear_socio(client):
    contador = {"n": 0}

    def _crear(activo: bool = True, **extra):
        contador["n"] += 1
        datos = {"nombre": f"Socio {contador['n']}", "email": f"socio{contador['n']}@mail.com",
                 "activo": activo, **extra}
        r = client.post("/socios", json=datos)
        assert r.status_code == 201, r.text
        return r.json()

    return _crear


@pytest.fixture
def crear_libro(client):
    contador = {"n": 0}

    def _crear(stock: int = 5, **extra):
        contador["n"] += 1
        datos = {"titulo": f"Libro {contador['n']}", "isbn": f"978-{contador['n']:06d}",
                 "stock": stock, "anio": 2000, **extra}
        r = client.post("/libros", json=datos)
        assert r.status_code == 201, r.text
        return r.json()

    return _crear
