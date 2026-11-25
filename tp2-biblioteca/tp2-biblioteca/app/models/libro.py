from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.autor import AutorRead
from app.models.libro_autor import LibroAutor

if TYPE_CHECKING:
    from app.models.autor import Autor
    from app.models.prestamo import Prestamo


class LibroBase(SQLModel):
    titulo: str = Field(min_length=1)
    isbn: str = Field(min_length=1)
    stock: int = Field(default=0, ge=0)  # ge=0 -> la API rechaza stock negativo con 422
    anio: int | None = None


class Libro(LibroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    isbn: str = Field(unique=True, index=True)

    autores: list["Autor"] = Relationship(back_populates="libros", link_model=LibroAutor)
    prestamos: list["Prestamo"] = Relationship(back_populates="libro")


class LibroCreate(LibroBase):
    pass


class LibroUpdate(SQLModel):
    titulo: str | None = Field(default=None, min_length=1)
    isbn: str | None = Field(default=None, min_length=1)
    stock: int | None = Field(default=None, ge=0)
    anio: int | None = None


class LibroRead(LibroBase):
    id: int


class LibroConAutores(LibroRead):
    """Respuesta de un libro que incluye la lista de sus autores."""
    autores: list[AutorRead] = []
