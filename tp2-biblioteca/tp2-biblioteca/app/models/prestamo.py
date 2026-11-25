from datetime import date
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.libro import Libro
    from app.models.socio import Socio


class Prestamo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    socio_id: int = Field(foreign_key="socio.id", index=True)
    libro_id: int = Field(foreign_key="libro.id", index=True)
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: date | None = None  # None = préstamo activo
    multa: int = 0

    socio: "Socio" = Relationship(back_populates="prestamos")
    libro: "Libro" = Relationship(back_populates="prestamos")


class PrestamoCreate(SQLModel):
    socio_id: int
    libro_id: int
    # Opcional: si no se manda, se usa la fecha de hoy.
    # Permitirla en el body facilita probar préstamos vencidos.
    fecha_prestamo: date | None = None


class PrestamoDevolucion(SQLModel):
    # Opcional: si no se manda, se devuelve hoy.
    fecha_devolucion: date | None = None


class PrestamoRead(SQLModel):
    id: int
    socio_id: int
    libro_id: int
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: date | None
    multa: int
