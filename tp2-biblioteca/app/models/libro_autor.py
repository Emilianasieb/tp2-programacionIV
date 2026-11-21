from sqlmodel import Field, SQLModel


class LibroAutor(SQLModel, table=True):
    """Tabla intermedia de la relación N-N entre Libro y Autor.

    La clave primaria es compuesta (libro_id, autor_id), así que el mismo
    autor no puede quedar asociado dos veces al mismo libro.
    """
    __tablename__ = "libro_autor"

    libro_id: int = Field(foreign_key="libro.id", primary_key=True)
    autor_id: int = Field(foreign_key="autor.id", primary_key=True)
