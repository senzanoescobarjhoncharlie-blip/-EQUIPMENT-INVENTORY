from typing import Optional
from pydantic import BaseModel, Field


class UbicacionBase(BaseModel):
    """Datos base de la ubicación física de un equipo."""

    edificio: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre o identificador del edificio",
        examples=["Edificio Central"]
    )
    ambiente: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Ambiente, aula, laboratorio u oficina",
        examples=["Laboratorio de Cómputo 3"]
    )
    responsable: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Nombre del encargado o custodio del ambiente/equipo",
        examples=["Ing. Carlos Mendoza"]
    )


class UbicacionCreate(UbicacionBase):
    """Esquema para registrar o actualizar ubicación."""
    pass


class UbicacionUpdate(BaseModel):
    """Esquema para actualización parcial de ubicación."""

    edificio: Optional[str] = Field(None, min_length=1, max_length=100)
    ambiente: Optional[str] = Field(None, min_length=1, max_length=100)
    responsable: Optional[str] = Field(None, min_length=1, max_length=150)


class UbicacionResponse(UbicacionBase):
    """Esquema de salida para ubicación."""
    pass
