from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.database import get_session
from app.models import LibroConAutores, LibroCreate, LibroUpdate
from app.services import libros as service

router = APIRouter(prefix="/libros", tags=["Libros"])


@router.get("", response_model=list[LibroConAutores])
def listar_libros(
    disponibles: bool | None = Query(default=None, description="true = solo libros con stock > 0"),
    session: Session = Depends(get_session),
):
    return service.listar(session, disponibles)


@router.get("/{libro_id}", response_model=LibroConAutores)
def obtener_libro(libro_id: int, session: Session = Depends(get_session)):
    return service.obtener(session, libro_id)


@router.post("", response_model=LibroConAutores, status_code=status.HTTP_201_CREATED)
def crear_libro(datos: LibroCreate, session: Session = Depends(get_session)):
    return service.crear(session, datos)


@router.patch("/{libro_id}", response_model=LibroConAutores)
def actualizar_libro(libro_id: int, datos: LibroUpdate, session: Session = Depends(get_session)):
    return service.actualizar(session, libro_id, datos)


@router.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_libro(libro_id: int, session: Session = Depends(get_session)):
    service.eliminar(session, libro_id)


@router.post(
    "/{libro_id}/autores/{autor_id}",
    response_model=LibroConAutores,
    status_code=status.HTTP_201_CREATED,
)
def asociar_autor(libro_id: int, autor_id: int, session: Session = Depends(get_session)):
    return service.asociar_autor(session, libro_id, autor_id)
