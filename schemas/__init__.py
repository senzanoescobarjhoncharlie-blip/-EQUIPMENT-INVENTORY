"""Módulo de esquemas de datos Pydantic."""
from schemas.ubicacion import UbicacionBase, UbicacionCreate, UbicacionResponse
from schemas.mantenimiento import MantenimientoBase, MantenimientoCreate, MantenimientoResponse
from schemas.equipo import (
    EquipoBase,
    EquipoCreate,
    EquipoUpdate,
    EquipoResponse,
    EquipoListResponse,
)

__all__ = [
    "UbicacionBase",
    "UbicacionCreate",
    "UbicacionResponse",
    "MantenimientoBase",
    "MantenimientoCreate",
    "MantenimientoResponse",
    "EquipoBase",
    "EquipoCreate",
    "EquipoUpdate",
    "EquipoResponse",
    "EquipoListResponse",
]
