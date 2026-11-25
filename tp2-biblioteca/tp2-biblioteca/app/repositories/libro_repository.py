from sqlmodel import Session, select

from app.models import Autor, Libro


def listar(session: Session, disponibles: bool | None = None) -> list[Libro]:
    consulta = select(Libro)
    if disponibles is True:
        consulta = consulta.where(Libro.stock > 0)
    elif disponibles is False:
        consulta = consulta.where(Libro.stock == 0)
    return list(session.exec(consulta).all())


def buscar_por_id(session: Session, libro_id: int) -> Libro | None:
    return session.get(Libro, libro_id)


def buscar_por_isbn(session: Session, isbn: str) -> Libro | None:
    return session.exec(select(Libro).where(Libro.isbn == isbn)).first()


def guardar(session: Session, libro: Libro) -> Libro:
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro


def eliminar(session: Session, libro: Libro) -> None:
    libro.autores = []  # borra sus filas de libro_autor
    session.delete(libro)
    session.commit()


def agregar_autor(session: Session, libro: Libro, autor: Autor) -> Libro:
    libro.autores.append(autor)  # inserta una fila en libro_autor
    return guardar(session, libro)
