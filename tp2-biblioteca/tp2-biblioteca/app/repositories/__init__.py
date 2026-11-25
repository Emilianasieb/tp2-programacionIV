"""Capa de acceso a datos.

Es la única capa que habla con la base: arma las consultas (select),
agrega, borra y confirma los cambios (commit). Los services le piden
datos o le piden guardar, pero no saben cómo se hace.
"""
