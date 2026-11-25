from sqlmodel import Session, select

from app.models import Socio


def listar(session: Session) -> list[Socio]:
    return list(session.exec(select(Socio)).all())


def buscar_por_id(session: Session, socio_id: int) -> Socio | None:
    return session.get(Socio, socio_id)


def buscar_por_email(session: Session, email: str) -> Socio | None:
    return session.exec(select(Socio).where(Socio.email == email)).first()


def guardar(session: Session, socio: Socio) -> Socio:
    session.add(socio)
    session.commit()
    session.refresh(socio)
    return socio


def eliminar(session: Session, socio: Socio) -> None:
    session.delete(socio)
    session.commit()
