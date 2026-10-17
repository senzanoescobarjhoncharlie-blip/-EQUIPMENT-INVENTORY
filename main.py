import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.v1.router import api_router
from core.config import settings
from core.database import check_database_connection, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo de eventos de ciclo de vida de la aplicación."""
    # Inicio: lazy init
    yield
    # Cierre: liberar conexión MongoDB
    close_mongo_connection()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "API REST desarrollada con FastAPI y MongoDB para la administración de "
        "equipos informáticos institucionales, registrando características técnicas, "
        "ubicaciones físicas y responsables, así como el historial de mantenimientos."
    ),
    openapi_tags=[
        {
            "name": "Equipos Informáticos",
            "description": "Operaciones CRUD, búsqueda por serie/código/modelo, filtros y mantenimientos."
        },
        {
            "name": "Sistema",
            "description": "Verificación de estado de salud y metadatos de la API."
        }
    ],
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de rutas v1
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Sistema"], summary="Información general de la API")
def raiz():
    """Ruta raíz de bienvenida."""
    return {
        "mensaje": "Sistema de Inventario de Equipos Informáticos funcionando"
    }


@app.get("/health", tags=["Sistema"], summary="Verificación de estado y conexión a base de datos")
def health_check():
    """Comprueba el estado del servicio y la conexión hacia MongoDB."""
    db_ok = check_database_connection()
    status_code = status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if db_ok else "unhealthy",
            "database": "connected" if db_ok else "disconnected",
            "version": settings.APP_VERSION
        }
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
