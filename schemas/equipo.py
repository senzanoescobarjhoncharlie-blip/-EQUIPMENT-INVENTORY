from typing import List, Optional
from pydantic import BaseModel, Field
from schemas.ubicacion import UbicacionCreate, UbicacionResponse, UbicacionUpdate
from schemas.mantenimiento import MantenimientoCreate, MantenimientoResponse


class EquipoBase(BaseModel):
    """Atributos base compartidos por un equipo informático."""

    codigo: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Código patrimonial o identificador único institucional",
        examples=["EQ-LAP-001"]
    )
    tipo: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Tipo de equipo (ej: Laptop, Servidor, Impresora, Switch, PC Escritorio)",
        examples=["Laptop"]
    )
    marca: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Marca del fabricante",
        examples=["Dell"]
    )
    modelo: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Modelo específico del fabricante",
        examples=["Latitude 5420"]
    )
    numero_serie: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Número de serie asignado por el fabricante",
        examples=["SN-DL5420-9988"]
    )
    fecha_adquisicion: str = Field(
        ...,
        description="Fecha de compra o ingreso en formato YYYY-MM-DD",
        examples=["2024-02-15"]
    )
    estado: str = Field(
        default="Operativo",
        description="Estado actual del equipo (ej: Operativo, En Mantenimiento, De Baja, En Reparación)",
        examples=["Operativo"]
    )
    caracteristicas: List[str] = Field(
        default_factory=list,
        description="Lista de especificaciones técnicas del equipo",
        examples=[["Intel Core i7 11th Gen", "16 GB RAM DDR4", "SSD 512GB NVMe", "Pantalla 14 FHD"]]
    )


class EquipoCreate(EquipoBase):
    """Esquema para registrar un nuevo equipo."""

    ubicacion: UbicacionCreate = Field(
        ...,
        description="Objeto con los datos de ubicación física y responsable del equipo"
    )
    mantenimientos: List[MantenimientoCreate] = Field(
        default_factory=list,
        description="Historial inicial de mantenimientos (opcional)"
    )


class EquipoUpdate(BaseModel):
    """Esquema para modificar la información de un equipo existente."""

    codigo: Optional[str] = Field(None, min_length=2, max_length=50)
    tipo: Optional[str] = Field(None, min_length=2, max_length=50)
    marca: Optional[str] = Field(None, min_length=2, max_length=50)
    modelo: Optional[str] = Field(None, min_length=1, max_length=100)
    numero_serie: Optional[str] = Field(None, min_length=2, max_length=100)
    fecha_adquisicion: Optional[str] = Field(None)
    estado: Optional[str] = Field(None)
    caracteristicas: Optional[List[str]] = Field(None)
    ubicacion: Optional[UbicacionUpdate] = Field(None)


class EquipoResponse(EquipoBase):
    """Esquema para devolver la información completa de un equipo."""

    id: str = Field(..., description="Identificador único generado por la base de datos (ObjectId)")
    ubicacion: UbicacionResponse = Field(..., description="Ubicación física y responsable")
    mantenimientos: List[MantenimientoResponse] = Field(
        default_factory=list,
        description="Historial de mantenimientos realizados"
    )

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "id": "6614a93f412d2b588390b3e1",
                "codigo": "EQ-LAP-001",
                "tipo": "Laptop",
                "marca": "Dell",
                "modelo": "Latitude 5420",
                "numero_serie": "SN-DL5420-9988",
                "fecha_adquisicion": "2024-02-15",
                "estado": "Operativo",
                "caracteristicas": [
                    "Intel Core i7 11th Gen",
                    "16 GB RAM DDR4",
                    "SSD 512GB NVMe"
                ],
                "ubicacion": {
                    "edificio": "Edificio Central",
                    "ambiente": "Laboratorio de Cómputo 3",
                    "responsable": "Ing. Carlos Mendoza"
                },
                "mantenimientos": [
                    {
                        "id": "m-001",
                        "fecha": "2025-01-10",
                        "tipo": "Preventivo",
                        "descripcion": "Limpieza general interna y cambio de pasta térmica",
                        "tecnico": "Téc. Roberto Gómez",
                        "costo": 35.0
                    }
                ]
            }
        }
    }


class EquipoListResponse(BaseModel):
    """Esquema para respuestas de listado con metadatos."""

    total: int = Field(..., description="Total de equipos encontrados")
    equipos: List[EquipoResponse] = Field(..., description="Lista de equipos")
