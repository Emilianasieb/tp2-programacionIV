from sqlmodel import Session, select

from app.models import Prestamo, Socio, SocioCreate, SocioUpdate
from app.services.errores import Conflicto, NoEncontrado


def listar(session: Session) -> list[Socio]:
    return list(session.exec(select(Socio)).all())


def obtener(session: Session, socio_id: int) -> Socio:
    socio = session.get(Socio, socio_id)
    if socio is None:
        raise NoEncontrado(f"Socio {socio_id} no encontrado")
    return socio


def _validar_email_unico(session: Session, email: str, excluir_id: int | None = None) -> None:
    """Regla 8: email duplicado -> 409."""
    existente = session.exec(select(Socio).where(Socio.email == email)).first()
    if existente is not None and existente.id != excluir_id:
        raise Conflicto(f"Ya existe un socio con email {email}")


def crear(session: Session, datos: SocioCreate) -> Socio:
    _validar_email_unico(session, datos.email)
    socio = Socio.model_validate(datos)
    session.add(socio)
    session.commit()
    session.refresh(socio)
    return socio


def actualizar(session: Session, socio_id: int, datos: SocioUpdate) -> Socio:
    socio = obtener(session, socio_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "email" in cambios:
        _validar_email_unico(session, cambios["email"], excluir_id=socio_id)
    socio.sqlmodel_update(cambios)
    session.add(socio)
    session.commit()
    session.refresh(socio)
    return socio


def eliminar(session: Session, socio_id: int) -> None:
    socio = obtener(session, socio_id)
    tiene_prestamos = session.exec(
        select(Prestamo).where(Prestamo.socio_id == socio_id)
    ).first()
    if tiene_prestamos is not None:
        raise Conflicto(
            "No se puede borrar un socio con préstamos registrados; se puede marcar como inactivo"
        )
    session.delete(socio)
    session.commit()


def prestamos_de_socio(
    session: Session, socio_id: int, activos: bool | None = None
) -> list[Prestamo]:
    obtener(session, socio_id)  # 404 si el socio no existe
    consulta = select(Prestamo).where(Prestamo.socio_id == socio_id)
    if activos is True:
        consulta = consulta.where(Prestamo.fecha_devolucion == None)  # noqa: E711
    elif activos is False:
        consulta = consulta.where(Prestamo.fecha_devolucion != None)  # noqa: E711
    return list(session.exec(consulta).all())
