from sqlmodel import Session

from app.models import Prestamo, Socio, SocioCreate, SocioUpdate
from app.repositories import prestamo_repository
from app.repositories import socio_repository as repo
from app.services.errores import Conflicto, NoEncontrado


def listar(session: Session) -> list[Socio]:
    return repo.listar(session)


def obtener(session: Session, socio_id: int) -> Socio:
    socio = repo.buscar_por_id(session, socio_id)
    if socio is None:
        raise NoEncontrado(f"Socio {socio_id} no encontrado")
    return socio


def _validar_email_unico(session: Session, email: str, excluir_id: int | None = None) -> None:
    """Regla 8: email duplicado -> 409."""
    existente = repo.buscar_por_email(session, email)
    if existente is not None and existente.id != excluir_id:
        raise Conflicto(f"Ya existe un socio con email {email}")


def crear(session: Session, datos: SocioCreate) -> Socio:
    _validar_email_unico(session, datos.email)
    return repo.guardar(session, Socio.model_validate(datos))


def actualizar(session: Session, socio_id: int, datos: SocioUpdate) -> Socio:
    socio = obtener(session, socio_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "email" in cambios:
        _validar_email_unico(session, cambios["email"], excluir_id=socio_id)
    socio.sqlmodel_update(cambios)
    return repo.guardar(session, socio)


def eliminar(session: Session, socio_id: int) -> None:
    socio = obtener(session, socio_id)
    if prestamo_repository.existe_para_socio(session, socio_id):
        raise Conflicto(
            "No se puede borrar un socio con préstamos registrados; se puede marcar como inactivo"
        )
    repo.eliminar(session, socio)


def prestamos_de_socio(
    session: Session, socio_id: int, activos: bool | None = None
) -> list[Prestamo]:
    obtener(session, socio_id)  # 404 si el socio no existe
    return prestamo_repository.listar_por_socio(session, socio_id, activos)
