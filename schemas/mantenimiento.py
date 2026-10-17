from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class MantenimientoBase(BaseModel):
    """Datos base de un registro de mantenimiento."""

    fecha: str = Field(
        ...,
        description="Fecha del mantenimiento en formato YYYY-MM-DD",
        examples=["2025-03-10"]
    )
    tipo: str = Field(
        ...,
        description="Tipo de mantenimiento (ej: Preventivo, Correctivo)",
        examples=["Preventivo"]
    )
    descripcion: str = Field(
        ...,
        min_length=3,
        description="Detalle técnico de las tareas realizadas",
        examples=["Limpieza interna, cambio de pasta térmica y actualización de BIOS"]
    )
    tecnico: str = Field(
        ...,
        min_length=2,
        description="Nombre del técnico o empresa responsable",
        examples=["Téc. Roberto Gómez"]
    )
    costo: Optional[float] = Field(
        default=0.0,
        ge=0,
        description="Costo del mantenimiento en moneda local o USD",
        examples=[35.50]
    )


class MantenimientoCreate(MantenimientoBase):
    """Esquema para crear un nuevo registro de mantenimiento."""

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid4())[:8],
        description="Identificador único del mantenimiento"
    )


class MantenimientoResponse(MantenimientoBase):
    """Esquema de salida de un mantenimiento."""

    id: Optional[str] = Field(
        default=None,
        description="Identificador del mantenimiento"
    )
