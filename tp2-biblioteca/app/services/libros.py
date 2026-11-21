from sqlmodel import Session, select

from app.models import Libro, LibroCreate, LibroUpdate, Prestamo
from app.services import autores as autores_service
from app.services.errores import Conflicto, NoEncontrado


def listar(session: Session, disponibles: bool | None = None) -> list[Libro]:
    consulta = select(Libro)
    if disponibles is True:
        consulta = consulta.where(Libro.stock > 0)
    elif disponibles is False:
        consulta = consulta.where(Libro.stock == 0)
    return list(session.exec(consulta).all())


def obtener(session: Session, libro_id: int) -> Libro:
    libro = session.get(Libro, libro_id)
    if libro is None:
        raise NoEncontrado(f"Libro {libro_id} no encontrado")
    return libro


def _validar_isbn_unico(session: Session, isbn: str, excluir_id: int | None = None) -> None:
    """Regla 8: ISBN duplicado -> 409."""
    existente = session.exec(select(Libro).where(Libro.isbn == isbn)).first()
    if existente is not None and existente.id != excluir_id:
        raise Conflicto(f"Ya existe un libro con ISBN {isbn}")


def crear(session: Session, datos: LibroCreate) -> Libro:
    _validar_isbn_unico(session, datos.isbn)
    libro = Libro.model_validate(datos)
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro


def actualizar(session: Session, libro_id: int, datos: LibroUpdate) -> Libro:
    libro = obtener(session, libro_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "isbn" in cambios:
        _validar_isbn_unico(session, cambios["isbn"], excluir_id=libro_id)
    libro.sqlmodel_update(cambios)
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro


def eliminar(session: Session, libro_id: int) -> None:
    libro = obtener(session, libro_id)
    # Si el libro tiene préstamos, borrarlo dejaría préstamos apuntando a nada
    tiene_prestamos = session.exec(
        select(Prestamo).where(Prestamo.libro_id == libro_id)
    ).first()
    if tiene_prestamos is not None:
        raise Conflicto("No se puede borrar un libro que tiene préstamos registrados")
    libro.autores = []
    session.delete(libro)
    session.commit()


def asociar_autor(session: Session, libro_id: int, autor_id: int) -> Libro:
    libro = obtener(session, libro_id)
    autor = autores_service.obtener(session, autor_id)
    if autor in libro.autores:
        raise Conflicto(f"El autor {autor_id} ya está asociado al libro {libro_id}")
    libro.autores.append(autor)
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro
