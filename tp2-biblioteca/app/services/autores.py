from sqlmodel import Session, select

from app.models import Autor, AutorCreate, AutorUpdate
from app.services.errores import NoEncontrado


def listar(session: Session) -> list[Autor]:
    return list(session.exec(select(Autor)).all())


def obtener(session: Session, autor_id: int) -> Autor:
    autor = session.get(Autor, autor_id)
    if autor is None:
        raise NoEncontrado(f"Autor {autor_id} no encontrado")
    return autor


def crear(session: Session, datos: AutorCreate) -> Autor:
    autor = Autor.model_validate(datos)
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor


def actualizar(session: Session, autor_id: int, datos: AutorUpdate) -> Autor:
    autor = obtener(session, autor_id)
    autor.sqlmodel_update(datos.model_dump(exclude_unset=True))
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor


def eliminar(session: Session, autor_id: int) -> None:
    autor = obtener(session, autor_id)
    # Vaciar la relación borra las filas de libro_autor de este autor
    autor.libros = []
    session.delete(autor)
    session.commit()
