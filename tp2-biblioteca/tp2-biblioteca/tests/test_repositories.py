"""Tests de la capa repositories: se prueban directo contra la base en memoria,
sin pasar por HTTP ni por los services."""
from datetime import date
from pathlib import Path

from app.models import Autor, Libro, Prestamo, Socio
from app.repositories import (
    autor_repository,
    libro_repository,
    prestamo_repository,
    socio_repository,
)


def test_guardar_asigna_id_y_buscar_por_id(session):
    autor = autor_repository.guardar(session, Autor(nombre="Borges"))
    assert autor.id is not None
    assert autor_repository.buscar_por_id(session, autor.id).nombre == "Borges"
    assert autor_repository.buscar_por_id(session, 999) is None


def test_libro_buscar_por_isbn_y_filtro_disponibles(session):
    libro_repository.guardar(session, Libro(titulo="A", isbn="111", stock=2))
    libro_repository.guardar(session, Libro(titulo="B", isbn="222", stock=0))

    assert libro_repository.buscar_por_isbn(session, "111").titulo == "A"
    assert libro_repository.buscar_por_isbn(session, "999") is None
    assert [l.titulo for l in libro_repository.listar(session, disponibles=True)] == ["A"]
    assert [l.titulo for l in libro_repository.listar(session, disponibles=False)] == ["B"]
    assert len(libro_repository.listar(session)) == 2


def test_socio_buscar_por_email(session):
    socio_repository.guardar(session, Socio(nombre="Ana", email="ana@mail.com"))
    assert socio_repository.buscar_por_email(session, "ana@mail.com").nombre == "Ana"
    assert socio_repository.buscar_por_email(session, "otro@mail.com") is None


def test_prestamo_consultas_por_socio_y_libro(session):
    socio = socio_repository.guardar(session, Socio(nombre="Ana", email="ana@mail.com"))
    libro = libro_repository.guardar(session, Libro(titulo="A", isbn="1", stock=5))
    hoy = date(2026, 11, 1)

    def nuevo(devuelto: bool) -> Prestamo:
        p = Prestamo(socio_id=socio.id, libro_id=libro.id, fecha_prestamo=hoy,
                     fecha_vencimiento=hoy, fecha_devolucion=hoy if devuelto else None)
        return prestamo_repository.guardar_con_libro(session, p, libro)

    assert not prestamo_repository.existe_para_socio(session, socio.id)
    nuevo(devuelto=False)
    nuevo(devuelto=False)
    nuevo(devuelto=True)

    assert prestamo_repository.contar_activos_por_socio(session, socio.id) == 2
    assert len(prestamo_repository.listar_por_socio(session, socio.id, activos=True)) == 2
    assert len(prestamo_repository.listar_por_socio(session, socio.id, activos=False)) == 1
    assert prestamo_repository.existe_para_socio(session, socio.id)
    assert prestamo_repository.existe_para_libro(session, libro.id)
    assert not prestamo_repository.existe_para_libro(session, 999)


def test_los_services_no_acceden_a_la_base_directamente():
    """Regla de arquitectura: solo los repositories pueden usar select/commit/etc."""
    prohibido = ["select(", "session.exec", "session.add", "session.commit",
                 "session.get", "session.delete", "session.refresh"]
    carpeta = Path(__file__).parent.parent / "app" / "services"
    for archivo in carpeta.glob("*.py"):
        codigo = archivo.read_text(encoding="utf-8")
        for texto in prohibido:
            assert texto not in codigo, f"{archivo.name} usa {texto}"
