import re
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pymongo.errors import PyMongoError

from core.database import get_equipos_collection
from schemas.equipo import EquipoCreate, EquipoUpdate, EquipoResponse, EquipoListResponse
from utils.errors import validate_object_id
from utils.serializers import serialize_doc, serialize_list

router = APIRouter(prefix="/equipos", tags=["Equipos"])


@router.post(
    "",
    response_model=EquipoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo equipo"
)
def crear_equipo(equipo_in: EquipoCreate):
    collection = get_equipos_collection()
    try:
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
                    detail=f"Ya existe un equipo con el codigo '{equipo_in.codigo}'"
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un equipo con el numero de serie '{equipo_in.numero_serie}'"
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
            detail=f"Error en la base de datos: {str(err)}"
        )


@router.get(
    "",
    response_model=EquipoListResponse,
    summary="Listar todos los equipos"
)
def listar_equipos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tipo: Optional[str] = None,
    marca: Optional[str] = None,
    estado: Optional[str] = None
):
    collection = get_equipos_collection()
    filtro = {}
    if tipo:
        filtro["tipo"] = {"$regex": f"^{re.escape(tipo.strip())}$", "$options": "i"}
    if marca:
        filtro["marca"] = {"$regex": f"^{re.escape(marca.strip())}$", "$options": "i"}
    if estado:
        filtro["estado"] = {"$regex": f"^{re.escape(estado.strip())}$", "$options": "i"}

    try:
        total = collection.count_documents(filtro)
        cursor = collection.find(filtro).skip(skip).limit(limit)
        return {
            "total": total,
            "equipos": serialize_list(list(cursor))
        }
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar equipos: {str(err)}"
        )


@router.get(
    "/{id}",
    response_model=EquipoResponse,
    summary="Consultar un equipo por ID"
)
def consultar_equipo(id: str):
    object_id = validate_object_id(id)
    collection = get_equipos_collection()
    try:
        equipo = collection.find_one({"_id": object_id})
        if not equipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Equipo con ID '{id}' no encontrado"
            )
        return serialize_doc(equipo)
    except HTTPException:
        raise
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar equipo: {str(err)}"
        )


@router.put(
    "/{id}",
    response_model=EquipoResponse,
    summary="Modificar la informacion de un equipo"
)
def modificar_equipo(id: str, equipo_in: EquipoUpdate):
    object_id = validate_object_id(id)
    collection = get_equipos_collection()
    try:
        equipo_actual = collection.find_one({"_id": object_id})
        if not equipo_actual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Equipo con ID '{id}' no encontrado"
            )

        datos_actualizar = equipo_in.model_dump(exclude_unset=True)
        if not datos_actualizar:
            return serialize_doc(equipo_actual)

        if "ubicacion" in datos_actualizar:
            ubicacion_actual = equipo_actual.get("ubicacion", {})
            ubicacion_actual.update(datos_actualizar["ubicacion"])
            datos_actualizar["ubicacion"] = ubicacion_actual

        collection.update_one({"_id": object_id}, {"$set": datos_actualizar})
        return serialize_doc(collection.find_one({"_id": object_id}))
    except HTTPException:
        raise
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al modificar equipo: {str(err)}"
        )


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar un equipo"
)
def eliminar_equipo(id: str):
    object_id = validate_object_id(id)
    collection = get_equipos_collection()
    try:
        resultado = collection.delete_one({"_id": object_id})
        if resultado.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Equipo con ID '{id}' no encontrado"
            )
        return {"mensaje": "Equipo eliminado correctamente", "id": id, "eliminado": True}
    except HTTPException:
        raise
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar equipo: {str(err)}"
        )




