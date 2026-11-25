from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.database import get_session
from app.models import AutorCreate, AutorRead, AutorUpdate
from app.services import autores as service

router = APIRouter(prefix="/autores", tags=["Autores"])


@router.get("", response_model=list[AutorRead])
def listar_autores(session: Session = Depends(get_session)):
    return service.listar(session)


@router.get("/{autor_id}", response_model=AutorRead)
def obtener_autor(autor_id: int, session: Session = Depends(get_session)):
    return service.obtener(session, autor_id)


@router.post("", response_model=AutorRead, status_code=status.HTTP_201_CREATED)
def crear_autor(datos: AutorCreate, session: Session = Depends(get_session)):
    return service.crear(session, datos)


@router.patch("/{autor_id}", response_model=AutorRead)
def actualizar_autor(autor_id: int, datos: AutorUpdate, session: Session = Depends(get_session)):
    return service.actualizar(session, autor_id, datos)


@router.delete("/{autor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_autor(autor_id: int, session: Session = Depends(get_session)):
    service.eliminar(session, autor_id)
