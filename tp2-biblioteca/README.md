# Sistema de Biblioteca (FastAPI + SQLModel)

API REST para gestionar el catálogo de una biblioteca (autores, libros, socios) y sus préstamos, con reglas de negocio y tests.

## Requisitos
- Python 3.11 o superior

## Cómo correrlo

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Documentación interactiva (Swagger): http://127.0.0.1:8000/docs

Por defecto usa SQLite en `./biblioteca.db` (se crea solo al arrancar). Para usar otra base se define la variable `DATABASE_URL` (ver `.env.example`), por ejemplo `postgresql://usuario:clave@localhost/biblioteca` (en ese caso hay que instalar también `psycopg2-binary`).

## Cómo testear

```bash
pytest
```

Los tests usan una base SQLite **en memoria** nueva para cada test, así que no tocan la base real. `pytest.ini` ya activa el reporte de cobertura (`--cov=app`). Resultado actual: **44 tests, cobertura 99 %**.

Para ver la cobertura en HTML: `pytest --cov-report=html` y abrir `htmlcov/index.html`.

## Estructura

```
app/
  main.py            # crea la app, registra routers y traduce errores a HTTP
  database.py        # engine y dependencia get_session
  models/            # tablas SQLModel y esquemas Create / Update / Read
  routers/           # endpoints, uno por entidad (sin lógica de negocio)
  services/          # reglas de negocio y acceso a datos
    errores.py       # NoEncontrado (404), Conflicto (409), Prohibido (403)
tests/               # pytest, un archivo por entidad
```

Flujo de una request: **router** (recibe y valida el JSON) → **service** (aplica reglas, lanza un error de dominio si algo no se cumple) → `main.py` convierte ese error en el código HTTP.

## Modelo de datos

| Entidad | Campos |
|---|---|
| `Autor` | id, nombre, nacionalidad |
| `Libro` | id, titulo, isbn (único), stock (≥ 0), anio |
| `LibroAutor` | libro_id, autor_id (clave primaria compuesta) |
| `Socio` | id, nombre, email (único), activo |
| `Prestamo` | id, socio_id, libro_id, fecha_prestamo, fecha_vencimiento, fecha_devolucion (null = activo), multa |

Relaciones: Libro N-N Autor (a través de `LibroAutor`), Préstamo N-1 Socio, Préstamo N-1 Libro.

## Endpoints

| Método | Ruta | Descripción | Éxito |
|---|---|---|---|
| GET / POST | `/autores` | Listar / crear | 200 / 201 |
| GET / PATCH / DELETE | `/autores/{id}` | Ver / modificar / borrar | 200 / 200 / 204 |
| GET / POST | `/libros` | Listar (incluye autores) / crear | 200 / 201 |
| GET | `/libros?disponibles=true` | Libros con stock > 0 (`false` = sin stock) | 200 |
| GET / PATCH / DELETE | `/libros/{id}` | Ver / modificar / borrar | 200 / 200 / 204 |
| POST | `/libros/{id}/autores/{autor_id}` | Asocia un autor al libro | 201 |
| GET / POST | `/socios` | Listar / crear | 200 / 201 |
| GET / PATCH / DELETE | `/socios/{id}` | Ver / modificar / borrar | 200 / 200 / 204 |
| GET | `/socios/{id}/prestamos?activos=true` | Préstamos del socio (`true` = sin devolver) | 200 |
| GET | `/prestamos`, `/prestamos/{id}` | Listar / ver | 200 |
| POST | `/prestamos` | Registra un préstamo | 201 |
| POST | `/prestamos/{id}/devolucion` | Registra la devolución | 200 |

`POST /prestamos` recibe `{"socio_id": 1, "libro_id": 2}` y opcionalmente `"fecha_prestamo": "2026-11-01"` (si no, hoy).
`POST /prestamos/{id}/devolucion` acepta body vacío o `{"fecha_devolucion": "2026-11-20"}` (si no, hoy).

## Reglas de negocio

| # | Regla | Error | Dónde |
|---|---|---|---|
| 1 | Máximo 3 préstamos activos por socio | 409 | `services/prestamos.py` |
| 2 | Sin stock no se presta; al prestar se descuenta 1 | 409 | `services/prestamos.py` |
| 3 | Socio inactivo no puede pedir préstamos | 403 | `services/prestamos.py` |
| 4 | `fecha_vencimiento = fecha_prestamo + 14 días` | – | `services/prestamos.py` |
| 5 | Al devolver se repone stock y multa = $100 × días de atraso | – | `services/prestamos.py` |
| 6 | No se devuelve un préstamo ya devuelto | 409 | `services/prestamos.py` |
| 7 | Recurso inexistente | 404 | `obtener()` de cada service |
| 8 | ISBN o email duplicado (al crear y al modificar) | 409 | `services/libros.py`, `services/socios.py` |

Decisiones extra:
- Datos mal formados (stock negativo, email inválido, nombre vacío) → **422**, lo valida FastAPI/Pydantic antes de llegar al service.
- Asociar dos veces el mismo autor al mismo libro → 409.
- No se borra un libro ni un socio que tenga préstamos registrados → 409 (al socio se lo puede marcar `activo: false`).
- Devolver con fecha anterior a la del préstamo → 409.

## Pendiente (opcional de la consigna)
Roles `bibliotecario` y `socio` con autenticación: no implementado.
