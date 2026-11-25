from sqlmodel import Session

from app.models import Autor, AutorCreate, AutorUpdate
from app.repositories import autor_repository as repo
from app.services.errores import NoEncontrado


def listar(session: Session) -> list[Autor]:
    return repo.listar(session)


def obtener(session: Session, autor_id: int) -> Autor:
    autor = repo.buscar_por_id(session, autor_id)
    if autor is None:
        raise NoEncontrado(f"Autor {autor_id} no encontrado")
    return autor


def crear(session: Session, datos: AutorCreate) -> Autor:
    return repo.guardar(session, Autor.model_validate(datos))


def actualizar(session: Session, autor_id: int, datos: AutorUpdate) -> Autor:
    autor = obtener(session, autor_id)
    autor.sqlmodel_update(datos.model_dump(exclude_unset=True))
    return repo.guardar(session, autor)


def eliminar(session: Session, autor_id: int) -> None:
    repo.eliminar(session, obtener(session, autor_id))
