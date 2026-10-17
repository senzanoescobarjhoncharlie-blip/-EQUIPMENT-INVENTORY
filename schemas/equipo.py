import re
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from schemas.ubicacion import UbicacionCreate, UbicacionResponse, UbicacionUpdate
from schemas.mantenimiento import MantenimientoCreate, MantenimientoResponse

# Estados válidos normalizados permitidos
ESTADOS_PERMITIDOS = {
    "disponible",
    "asignado",
    "en_mantenimiento",
    "en mantenimiento",
    "dado_de_baja",
    "dado de baja",
    "operativo",
    "en_reparacion",
    "en reparacion",
}


def normalizar_texto_no_vacio(v: str, campo: str) -> str:
    """Valida que una cadena no esté vacía ni contenga solo espacios en blanco."""
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"El campo '{campo}' no puede estar vacío ni contener solo espacios.")
    return v.strip()


class EquipoBase(BaseModel):
    """Atributos base de un equipo informático institucional."""

    codigo: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Código institucional o patrimonial del equipo",
        examples=["EQ-LAP-001"]
    )
    tipo: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Categoría o tipo de equipo (ej: Computadora, Laptop, Impresora, Monitor, Servidor)",
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
        description="Modelo comercial del equipo",
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
        description="Fecha de adquisición en formato YYYY-MM-DD",
        examples=["2024-02-15"]
    )
    estado: str = Field(
        default="disponible",
        description="Estado actual del equipo (ej: disponible, asignado, en_mantenimiento, dado_de_baja, operativo)",
        examples=["disponible"]
    )
    caracteristicas: List[str] = Field(
        default_factory=list,
        description="Lista de características técnicas del equipo",
        examples=[["Intel Core i7 11th Gen", "16 GB RAM DDR4", "SSD 512GB NVMe"]]
    )

    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, v: str) -> str:
        return normalizar_texto_no_vacio(v, "codigo")

    @field_validator("numero_serie")
    @classmethod
    def validar_numero_serie(cls, v: str) -> str:
        return normalizar_texto_no_vacio(v, "numero_serie")

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v: str) -> str:
        return normalizar_texto_no_vacio(v, "tipo")

    @field_validator("marca")
    @classmethod
    def validar_marca(cls, v: str) -> str:
        return normalizar_texto_no_vacio(v, "marca")

    @field_validator("modelo")
    @classmethod
    def validar_modelo(cls, v: str) -> str:
        return normalizar_texto_no_vacio(v, "modelo")

    @field_validator("fecha_adquisicion")
    @classmethod
    def validar_fecha(cls, v: str) -> str:
        v_limpia = normalizar_texto_no_vacio(v, "fecha_adquisicion")
        try:
            datetime.strptime(v_limpia, "%Y-%m-%d")
        except ValueError:
            raise ValueError("El campo 'fecha_adquisicion' debe tener un formato válido de fecha (YYYY-MM-DD).")
        return v_limpia

    @field_validator("estado")
    @classmethod
    def validar_y_normalizar_estado(cls, v: str) -> str:
        v_limpia = normalizar_texto_no_vacio(v, "estado").lower()
        # Normalizar separadores
        normalizado = v_limpia.replace(" ", "_")
        if normalizado not in {s.replace(" ", "_") for s in ESTADOS_PERMITIDOS}:
            raise ValueError(
                f"Estado '{v}' no válido. Opciones permitidas: disponible, asignado, en_mantenimiento, dado_de_baja, operativo."
            )
        return normalizado


class EquipoCreate(EquipoBase):
    """Esquema para registrar un nuevo equipo en el inventario."""

    ubicacion: UbicacionCreate = Field(
        ...,
        description="Objeto con los datos de ubicación física y responsable del equipo"
    )
    mantenimientos: List[MantenimientoCreate] = Field(
        default_factory=list,
        description="Historial inicial de mantenimientos (opcional)"
    )


class EquipoUpdate(BaseModel):
    """Esquema para modificar parcialmente los datos de un equipo existente."""

    codigo: Optional[str] = Field(None, min_length=2, max_length=50)
    tipo: Optional[str] = Field(None, min_length=2, max_length=50)
    marca: Optional[str] = Field(None, min_length=2, max_length=50)
    modelo: Optional[str] = Field(None, min_length=1, max_length=100)
    numero_serie: Optional[str] = Field(None, min_length=2, max_length=100)
    fecha_adquisicion: Optional[str] = Field(None)
    estado: Optional[str] = Field(None)
    caracteristicas: Optional[List[str]] = Field(None)
    ubicacion: Optional[UbicacionUpdate] = Field(None)

    @field_validator("codigo", "numero_serie", "tipo", "marca", "modelo", mode="before")
    @classmethod
    def validar_campos_opcionales(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not isinstance(v, str) or not v.strip():
                raise ValueError("Los valores a actualizar no pueden estar vacíos ni contener solo espacios.")
            return v.strip()
        return v

    @field_validator("fecha_adquisicion")
    @classmethod
    def validar_fecha_opcional(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_limpia = normalizar_texto_no_vacio(v, "fecha_adquisicion")
            try:
                datetime.strptime(v_limpia, "%Y-%m-%d")
            except ValueError:
                raise ValueError("El campo 'fecha_adquisicion' debe tener un formato válido de fecha (YYYY-MM-DD).")
            return v_limpia
        return v

    @field_validator("estado")
    @classmethod
    def validar_estado_opcional(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_limpia = normalizar_texto_no_vacio(v, "estado").lower()
            normalizado = v_limpia.replace(" ", "_")
            if normalizado not in {s.replace(" ", "_") for s in ESTADOS_PERMITIDOS}:
                raise ValueError(
                    f"Estado '{v}' no válido. Opciones permitidas: disponible, asignado, en_mantenimiento, dado_de_baja, operativo."
                )
            return normalizado
        return v


class EquipoResponse(EquipoBase):
    """Esquema de salida con el identificador serializado y modelos anidados."""

    id: str = Field(..., description="Identificador único generado por MongoDB (ObjectId serializado a str)")
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
                "estado": "disponible",
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
    """Esquema para respuestas de listado paginado."""

    total: int = Field(..., description="Total de registros coincidentes")
    equipos: List[EquipoResponse] = Field(..., description="Lista de equipos en la página actual")
