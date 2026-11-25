from fastapi import APIRouter, Body, Depends, status
from sqlmodel import Session

from app.database import get_session
from app.models import PrestamoCreate, PrestamoDevolucion, PrestamoRead
from app.services import prestamos as service

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])


@router.get("", response_model=list[PrestamoRead])
def listar_prestamos(session: Session = Depends(get_session)):
    return service.listar(session)


@router.get("/{prestamo_id}", response_model=PrestamoRead)
def obtener_prestamo(prestamo_id: int, session: Session = Depends(get_session)):
    return service.obtener(session, prestamo_id)


@router.post("", response_model=PrestamoRead, status_code=status.HTTP_201_CREATED)
def registrar_prestamo(datos: PrestamoCreate, session: Session = Depends(get_session)):
    return service.registrar_prestamo(session, datos)


@router.post("/{prestamo_id}/devolucion", response_model=PrestamoRead)
def registrar_devolucion(
    prestamo_id: int,
    datos: PrestamoDevolucion | None = Body(default=None),
    session: Session = Depends(get_session),
):
    fecha = datos.fecha_devolucion if datos else None
    return service.registrar_devolucion(session, prestamo_id, fecha)
