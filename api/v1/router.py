from fastapi import APIRouter
from api.v1.endpoints.equipos import router as equipos_router

api_router = APIRouter()
api_router.include_router(equipos_router)
