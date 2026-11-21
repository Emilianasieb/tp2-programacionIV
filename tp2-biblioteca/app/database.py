"""Configuración de la base de datos y de la sesión."""
import os
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./biblioteca.db")

# check_same_thread=False solo hace falta con SQLite, porque FastAPI
# puede atender la request en un hilo distinto al que abrió la conexión.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def crear_tablas() -> None:
    # Importar los modelos registra las tablas en SQLModel.metadata
    from app import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependencia de FastAPI: abre una sesión por request y la cierra al final."""
    with Session(engine) as session:
        yield session
