from sqlmodel import Session, func, select

from app.models import Libro, Prestamo


def listar(session: Session) -> list[Prestamo]:
    return list(session.exec(select(Prestamo)).all())


def buscar_por_id(session: Session, prestamo_id: int) -> Prestamo | None:
    return session.get(Prestamo, prestamo_id)


def listar_por_socio(
    session: Session, socio_id: int, activos: bool | None = None
) -> list[Prestamo]:
    """Activo = sin fecha de devolución."""
    consulta = select(Prestamo).where(Prestamo.socio_id == socio_id)
    if activos is True:
        consulta = consulta.where(Prestamo.fecha_devolucion == None)  # noqa: E711
    elif activos is False:
        consulta = consulta.where(Prestamo.fecha_devolucion != None)  # noqa: E711
    return list(session.exec(consulta).all())


def contar_activos_por_socio(session: Session, socio_id: int) -> int:
    consulta = select(func.count()).select_from(Prestamo).where(
        Prestamo.socio_id == socio_id,
        Prestamo.fecha_devolucion == None,  # noqa: E711
    )
    return session.exec(consulta).one()


def existe_para_libro(session: Session, libro_id: int) -> bool:
    consulta = select(Prestamo.id).where(Prestamo.libro_id == libro_id).limit(1)
    return session.exec(consulta).first() is not None


def existe_para_socio(session: Session, socio_id: int) -> bool:
    consulta = select(Prestamo.id).where(Prestamo.socio_id == socio_id).limit(1)
    return session.exec(consulta).first() is not None


def guardar_con_libro(session: Session, prestamo: Prestamo, libro: Libro) -> Prestamo:
    """Guarda el préstamo y el cambio de stock del libro en UN solo commit.

    Así, o se graban las dos cosas o ninguna (transacción).
    """
    session.add(libro)
    session.add(prestamo)
    session.commit()
    session.refresh(prestamo)
    return prestamo
