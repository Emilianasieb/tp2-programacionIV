from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.database import get_session
from app.models import PrestamoRead, SocioCreate, SocioRead, SocioUpdate
from app.services import socios as service

router = APIRouter(prefix="/socios", tags=["Socios"])


@router.get("", response_model=list[SocioRead])
def listar_socios(session: Session = Depends(get_session)):
    return service.listar(session)


@router.get("/{socio_id}", response_model=SocioRead)
def obtener_socio(socio_id: int, session: Session = Depends(get_session)):
    return service.obtener(session, socio_id)


@router.post("", response_model=SocioRead, status_code=status.HTTP_201_CREATED)
def crear_socio(datos: SocioCreate, session: Session = Depends(get_session)):
    return service.crear(session, datos)


@router.patch("/{socio_id}", response_model=SocioRead)
def actualizar_socio(socio_id: int, datos: SocioUpdate, session: Session = Depends(get_session)):
    return service.actualizar(session, socio_id, datos)


@router.delete("/{socio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_socio(socio_id: int, session: Session = Depends(get_session)):
    service.eliminar(session, socio_id)


@router.get("/{socio_id}/prestamos", response_model=list[PrestamoRead])
def prestamos_del_socio(
    socio_id: int,
    activos: bool | None = Query(default=None, description="true = solo préstamos sin devolver"),
    session: Session = Depends(get_session),
):
    return service.prestamos_de_socio(session, socio_id, activos)
