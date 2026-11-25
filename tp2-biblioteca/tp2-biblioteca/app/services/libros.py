from sqlmodel import Session

from app.models import Libro, LibroCreate, LibroUpdate
from app.repositories import libro_repository as repo
from app.repositories import prestamo_repository
from app.services import autores as autores_service
from app.services.errores import Conflicto, NoEncontrado


def listar(session: Session, disponibles: bool | None = None) -> list[Libro]:
    return repo.listar(session, disponibles)


def obtener(session: Session, libro_id: int) -> Libro:
    libro = repo.buscar_por_id(session, libro_id)
    if libro is None:
        raise NoEncontrado(f"Libro {libro_id} no encontrado")
    return libro


def _validar_isbn_unico(session: Session, isbn: str, excluir_id: int | None = None) -> None:
    """Regla 8: ISBN duplicado -> 409."""
    existente = repo.buscar_por_isbn(session, isbn)
    if existente is not None and existente.id != excluir_id:
        raise Conflicto(f"Ya existe un libro con ISBN {isbn}")


def crear(session: Session, datos: LibroCreate) -> Libro:
    _validar_isbn_unico(session, datos.isbn)
    return repo.guardar(session, Libro.model_validate(datos))


def actualizar(session: Session, libro_id: int, datos: LibroUpdate) -> Libro:
    libro = obtener(session, libro_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "isbn" in cambios:
        _validar_isbn_unico(session, cambios["isbn"], excluir_id=libro_id)
    libro.sqlmodel_update(cambios)
    return repo.guardar(session, libro)


def eliminar(session: Session, libro_id: int) -> None:
    libro = obtener(session, libro_id)
    # Si el libro tiene préstamos, borrarlo dejaría préstamos apuntando a nada
    if prestamo_repository.existe_para_libro(session, libro_id):
        raise Conflicto("No se puede borrar un libro que tiene préstamos registrados")
    repo.eliminar(session, libro)


def asociar_autor(session: Session, libro_id: int, autor_id: int) -> Libro:
    libro = obtener(session, libro_id)
    autor = autores_service.obtener(session, autor_id)
    if autor in libro.autores:
        raise Conflicto(f"El autor {autor_id} ya está asociado al libro {libro_id}")
    return repo.agregar_autor(session, libro, autor)
