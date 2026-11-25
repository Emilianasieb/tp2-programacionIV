from sqlmodel import Session, select

from app.models import Autor


def listar(session: Session) -> list[Autor]:
    return list(session.exec(select(Autor)).all())


def buscar_por_id(session: Session, autor_id: int) -> Autor | None:
    return session.get(Autor, autor_id)


def guardar(session: Session, autor: Autor) -> Autor:
    """Inserta o actualiza el autor y devuelve la versión guardada (con id)."""
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor


def eliminar(session: Session, autor: Autor) -> None:
    # Vaciar la relación borra las filas de libro_autor de este autor
    autor.libros = []
    session.delete(autor)
    session.commit()
