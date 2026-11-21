"""Modelos de la base de datos y esquemas de entrada/salida.

Se importan todos acá para que SQLAlchemy pueda resolver las relaciones
(que están escritas como texto, por ejemplo "Libro") entre archivos distintos.
"""
from app.models.libro_autor import LibroAutor
from app.models.autor import Autor, AutorCreate, AutorRead, AutorUpdate
from app.models.libro import Libro, LibroConAutores, LibroCreate, LibroRead, LibroUpdate
from app.models.socio import Socio, SocioCreate, SocioRead, SocioUpdate
from app.models.prestamo import Prestamo, PrestamoCreate, PrestamoDevolucion, PrestamoRead

__all__ = [
    "LibroAutor",
    "Autor", "AutorCreate", "AutorRead", "AutorUpdate",
    "Libro", "LibroCreate", "LibroRead", "LibroUpdate", "LibroConAutores",
    "Socio", "SocioCreate", "SocioRead", "SocioUpdate",
    "Prestamo", "PrestamoCreate", "PrestamoRead", "PrestamoDevolucion",
]
