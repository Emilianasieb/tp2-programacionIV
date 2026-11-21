from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.database import crear_tablas
from app.routers import autores, libros, prestamos, socios
from app.services.errores import ErrorDominio


@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_tablas()  # crea las tablas al arrancar si no existen
    yield


app = FastAPI(
    title="Sistema de Biblioteca",
    description="API REST para gestionar el catálogo de una biblioteca y sus préstamos.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(ErrorDominio)
def manejar_error_dominio(request: Request, exc: ErrorDominio):
    """Traduce los errores de la capa services al código HTTP correspondiente."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detalle})


app.include_router(autores.router)
app.include_router(libros.router)
app.include_router(socios.router)
app.include_router(prestamos.router)


@app.get("/", tags=["Salud"])
def raiz():
    return {"mensaje": "API Sistema de Biblioteca. Documentación en /docs"}
