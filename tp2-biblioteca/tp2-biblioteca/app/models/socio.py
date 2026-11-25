import re
from typing import TYPE_CHECKING

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.prestamo import Prestamo

# Validación simple: algo@algo.algo (sin espacios)
PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar_email(valor: str | None) -> str | None:
    if valor is not None and not PATRON_EMAIL.match(valor):
        raise ValueError("email inválido")
    return valor


class SocioBase(SQLModel):
    nombre: str = Field(min_length=1)
    email: str
    activo: bool = True

    _validar_email = field_validator("email")(validar_email)


class Socio(SocioBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)

    prestamos: list["Prestamo"] = Relationship(back_populates="socio")


class SocioCreate(SocioBase):
    pass


class SocioUpdate(SQLModel):
    nombre: str | None = Field(default=None, min_length=1)
    email: str | None = None
    activo: bool | None = None

    _validar_email = field_validator("email")(validar_email)


class SocioRead(SocioBase):
    id: int
