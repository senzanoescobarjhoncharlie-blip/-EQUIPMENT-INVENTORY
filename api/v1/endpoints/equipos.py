import re
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from pymongo.errors import PyMongoError

from core.database import get_equipos_collection
from schemas.equipo import (
    EquipoCreate,
    EquipoResponse,
    EquipoListResponse,
)
from utils.mongo import validate_object_id, serialize_doc, serialize_list

router = APIRouter(prefix="/equipos", tags=["Equipos Informáticos"])


# ============================================================================
# 1. REGISTRAR EQUIPO
# ============================================================================
@router.post(
    "",
    response_model=EquipoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="1. Registrar equipo",
    description="Registra un nuevo equipo institucional en la colección 'equipos'. Valida unicidad en código y número de serie."
)
def registrar_equipo(equipo_in: EquipoCreate):
    collection = get_equipos_collection()

    try:
        # Validación de duplicidad para código y número de serie
        existente = collection.find_one({
            "$or": [
                {"codigo": equipo_in.codigo},
                {"numero_serie": equipo_in.numero_serie}
            ]
        })
        if existente:
            if existente.get("codigo") == equipo_in.codigo:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Conflicto: Ya existe un equipo registrado con el código '{equipo_in.codigo}'."
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Conflicto: Ya existe un equipo registrado con el número de serie '{equipo_in.numero_serie}'."
            )

        doc = equipo_in.model_dump()
        result = collection.insert_one(doc)
        creado = collection.find_one({"_id": result.inserted_id})
        return serialize_doc(creado)

    except HTTPException:
        raise
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos al registrar equipo: {str(err)}"
        )


# ============================================================================
# 2. LISTAR TODOS LOS EQUIPOS
# ============================================================================
@router.get(
    "",
    response_model=EquipoListResponse,
    summary="2. Listar todos los equipos",
    description="Retorna el listado de equipos con soporte para paginación razonable (skip y limit) y filtros opcionales."
)
def listar_equipos(
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir para paginación"),
    limit: int = Query(100, ge=1, le=500, description="Límite máximo de equipos a retornar por página"),
    tipo: Optional[str] = Query(None, description="Filtrar opcionalmente por tipo de equipo"),
    marca: Optional[str] = Query(None, description="Filtrar opcionalmente por marca"),
    estado: Optional[str] = Query(None, description="Filtrar opcionalmente por estado")
):
    collection = get_equipos_collection()

    filtro = {}
    if tipo and tipo.strip():
        filtro["tipo"] = {"$regex": f"^{re.escape(tipo.strip())}$", "$options": "i"}
    if marca and marca.strip():
        filtro["marca"] = {"$regex": f"^{re.escape(marca.strip())}$", "$options": "i"}
    if estado and estado.strip():
        filtro["estado"] = {"$regex": f"^{re.escape(estado.strip())}$", "$options": "i"}

    try:
        total = collection.count_documents(filtro)
        cursor = collection.find(filtro).skip(skip).limit(limit)
        equipos = list(cursor)
        return {
            "total": total,
            "equipos": serialize_list(equipos)
        }
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar equipos: {str(err)}"
        )


# ============================================================================
# 3. CONSULTAR UN EQUIPO POR IDENTIFICADOR
# ============================================================================
@router.get(
    "/{equipo_id}",
    response_model=EquipoResponse,
    summary="3. Consultar un equipo por identificador",
    description="Obtiene los datos completos de un equipo a partir de su ObjectId de MongoDB."
)
def consultar_equipo(equipo_id: str):
    object_id = validate_object_id(equipo_id)
    collection = get_equipos_collection()

    try:
        equipo = collection.find_one({"_id": object_id})
        if not equipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Equipo con identificador '{equipo_id}' no fue encontrado."
            )
        return serialize_doc(equipo)
    except HTTPException:
        raise
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar el equipo: {str(err)}"
        )
