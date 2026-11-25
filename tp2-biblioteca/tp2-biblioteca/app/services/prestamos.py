"""Reglas de negocio de los préstamos.

Todas las reglas viven acá: el router solo recibe la request y llama a
estas funciones, y el repository es el único que toca la base.
"""
from datetime import date, timedelta

from sqlmodel import Session

from app.models import Prestamo, PrestamoCreate
from app.repositories import prestamo_repository as repo
from app.services import libros as libros_service
from app.services import socios as socios_service
from app.services.errores import Conflicto, NoEncontrado, Prohibido

MAX_PRESTAMOS_ACTIVOS = 3   # Regla 1
DIAS_DE_PLAZO = 14          # Regla 4
MULTA_POR_DIA = 100         # Regla 5


def listar(session: Session) -> list[Prestamo]:
    return repo.listar(session)


def obtener(session: Session, prestamo_id: int) -> Prestamo:
    prestamo = repo.buscar_por_id(session, prestamo_id)
    if prestamo is None:
        raise NoEncontrado(f"Préstamo {prestamo_id} no encontrado")
    return prestamo


def calcular_multa(fecha_vencimiento: date, fecha_devolucion: date) -> int:
    """Regla 5: $100 por cada día de atraso; 0 si se devolvió a tiempo."""
    dias_atraso = (fecha_devolucion - fecha_vencimiento).days
    return max(dias_atraso, 0) * MULTA_POR_DIA


def registrar_prestamo(session: Session, datos: PrestamoCreate) -> Prestamo:
    # Regla 7: socio y libro tienen que existir (404)
    socio = socios_service.obtener(session, datos.socio_id)
    libro = libros_service.obtener(session, datos.libro_id)

    # Regla 3: socio inactivo -> 403
    if not socio.activo:
        raise Prohibido("El socio está inactivo y no puede pedir préstamos")

    # Regla 1: máximo 3 préstamos activos -> 409
    if repo.contar_activos_por_socio(session, socio.id) >= MAX_PRESTAMOS_ACTIVOS:
        raise Conflicto(f"El socio ya tiene {MAX_PRESTAMOS_ACTIVOS} préstamos activos")

    # Regla 2: sin stock -> 409; si hay, se descuenta 1
    if libro.stock <= 0:
        raise Conflicto("El libro no tiene stock disponible")
    libro.stock -= 1

    # Regla 4: el vencimiento es 14 días después del préstamo
    fecha_prestamo = datos.fecha_prestamo or date.today()
    prestamo = Prestamo(
        socio_id=socio.id,
        libro_id=libro.id,
        fecha_prestamo=fecha_prestamo,
        fecha_vencimiento=fecha_prestamo + timedelta(days=DIAS_DE_PLAZO),
    )

    # El stock y el préstamo se guardan juntos, en el mismo commit
    return repo.guardar_con_libro(session, prestamo, libro)


def registrar_devolucion(
    session: Session, prestamo_id: int, fecha_devolucion: date | None = None
) -> Prestamo:
    prestamo = obtener(session, prestamo_id)  # Regla 7

    # Regla 6: no se devuelve dos veces -> 409
    if prestamo.fecha_devolucion is not None:
        raise Conflicto("El préstamo ya fue devuelto")

    fecha = fecha_devolucion or date.today()
    if fecha < prestamo.fecha_prestamo:
        raise Conflicto("La fecha de devolución no puede ser anterior a la del préstamo")

    # Regla 5: se repone el stock y se calcula la multa
    prestamo.fecha_devolucion = fecha
    prestamo.multa = calcular_multa(prestamo.fecha_vencimiento, fecha)
    libro = libros_service.obtener(session, prestamo.libro_id)
    libro.stock += 1

    return repo.guardar_con_libro(session, prestamo, libro)
