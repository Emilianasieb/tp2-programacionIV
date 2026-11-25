"""Errores de dominio.

La capa services no conoce HTTP: lanza estos errores y main.py los
traduce al código HTTP que corresponde (404, 409, 403).
"""


class ErrorDominio(Exception):
    status_code = 400

    def __init__(self, detalle: str):
        super().__init__(detalle)
        self.detalle = detalle


class NoEncontrado(ErrorDominio):
    """Regla 7: recurso inexistente."""
    status_code = 404


class Conflicto(ErrorDominio):
    """Reglas 1, 2, 6 y 8: la operación choca con el estado actual de los datos."""
    status_code = 409


class Prohibido(ErrorDominio):
    """Regla 3: la operación no está permitida para ese socio."""
    status_code = 403
