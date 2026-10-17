import re
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pymongo.errors import PyMongoError

from core.database import get_equipos_collection
from schemas.equipo import (
    EquipoCreate,
    EquipoUpdate,
    EquipoResponse,
    EquipoListResponse,
)
from schemas.mantenimiento import MantenimientoCreate, MantenimientoResponse
from utils.errors import validate_object_id
from utils.serializers import serialize_doc, serialize_list

router = APIRouter(prefix="/equipos", tags=["Equipos Informáticos"])


@router.post(
    "",
    response_model=EquipoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="1. Registrar un nuevo equipo",
    description="Crea un nuevo documento de equipo en la colección de MongoDB asegurando unicidad en código y número de serie."
)
def crear_equipo(equipo_in: EquipoCreate):
    collection = get_equipos_collection()

    try:
        # Validación de duplicados para código y número de serie
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
                    detail=f"Ya existe un equipo registrado con el código '{equipo_in.codigo}'."
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un equipo registrado con el número de serie '{equipo_in.numero_serie}'."
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
            detail=f"Error en la base de datos al registrar el equipo: {str(err)}"
        )


@router.get(
    "",
    response_model=EquipoListResponse,
    summary="2. Listar todos los equipos",
    description="Devuelve la lista completa de equipos registrados en el inventario con soporte para paginación y filtros opcionales."
)
def listar_equipos(
    skip: int = Query(0, ge=0, description="Número de registros a omitir para paginación"),
    limit: int = Query(100, ge=1, le=500, description="Límite de registros a retornar"),
    tipo: Optional[str] = Query(None, description="Filtrar opcionalmente por tipo"),
    marca: Optional[str] = Query(None, description="Filtrar opcionalmente por marca"),
    estado: Optional[str] = Query(None, description="Filtrar opcionalmente por estado")
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


@router.get(
    "/buscar",
    response_model=List[EquipoResponse],
    summary="6. Buscar equipos por código, número de serie o modelo",
    description="Realiza una búsqueda flexible insensitiva a mayúsculas/minúsculas en los campos código, número de serie o modelo."
)
def buscar_equipos(
    q: Optional[str] = Query(None, description="Término a buscar (código, número de serie o modelo)"),
    termino: Optional[str] = Query(None, description="Alias alternativo para el término de búsqueda")
):
    search_str = q or termino
    if not search_str or not search_str.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar el parámetro 'q' o 'termino' para realizar la búsqueda."
        )

    collection = get_equipos_collection()
    pattern = re.escape(search_str.strip())

    filtro = {
        "$or": [
            {"codigo": {"$regex": pattern, "$options": "i"}},
            {"numero_serie": {"$regex": pattern, "$options": "i"}},
            {"modelo": {"$regex": pattern, "$options": "i"}}
        ]
    }

    try:
        resultados = list(collection.find(filtro))
        return serialize_list(resultados)
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la búsqueda de equipos: {str(err)}"
        )


@router.get(
    "/tipo/{tipo}",
    response_model=List[EquipoResponse],
    summary="7. Filtrar equipos por tipo",
    description="Retorna todos los equipos que correspondan a una categoría o tipo determinado (ej: Laptop, Servidor, Impresora)."
)
@router.get("/filtrar/tipo/{tipo}", response_model=List[EquipoResponse], include_in_schema=False)
def filtrar_por_tipo(tipo: str):
    collection = get_equipos_collection()
    filtro = {"tipo": {"$regex": f"^{re.escape(tipo.strip())}$", "$options": "i"}}

    try:
        resultados = list(collection.find(filtro))
        return serialize_list(resultados)
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al filtrar por tipo: {str(err)}"
        )


@router.get(
    "/marca/{marca}",
    response_model=List[EquipoResponse],
    summary="8. Filtrar equipos por marca",
    description="Retorna todos los equipos pertenecientes a una marca de fabricante (ej: Dell, HP, Lenovo)."
)
@router.get("/filtrar/marca/{marca}", response_model=List[EquipoResponse], include_in_schema=False)
def filtrar_por_marca(marca: str):
    collection = get_equipos_collection()
    filtro = {"marca": {"$regex": f"^{re.escape(marca.strip())}$", "$options": "i"}}

    try:
        resultados = list(collection.find(filtro))
        return serialize_list(resultados)
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al filtrar por marca: {str(err)}"
        )


@router.get(
    "/estado/{estado}",
    response_model=List[EquipoResponse],
    summary="9. Filtrar equipos por estado",
    description="Retorna todos los equipos en un estado específico (ej: Operativo, En Mantenimiento, De Baja)."
)
@router.get("/filtrar/estado/{estado}", response_model=List[EquipoResponse], include_in_schema=False)
def filtrar_por_estado(estado: str):
    collection = get_equipos_collection()
    filtro = {"estado": {"$regex": f"^{re.escape(estado.strip())}$", "$options": "i"}}

    try:
        resultados = list(collection.find(filtro))
        return serialize_list(resultados)
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al filtrar por estado: {str(err)}"
        )


@router.get(
    "/{id}",
    response_model=EquipoResponse,
    summary="3. Consultar un equipo mediante su identificador",
    description="Obtiene el detalle completo de un equipo a partir de su ID de MongoDB (ObjectId)."
)
def consultar_equipo(id: str):
    object_id = validate_object_id(id)
    collection = get_equipos_collection()

    try:
        equipo = collection.find_one({"_id": object_id})
        if not equipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Equipo con identificador '{id}' no fue encontrado."
            )
        return serialize_doc(equipo)
    except HTTPException:
        raise
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar el equipo: {str(err)}"
        )


@router.put(
    "/{id}",
    response_model=EquipoResponse,
    summary="4. Modificar la información de un equipo",
    description="Actualiza los datos de un equipo existente. Permite actualización parcial o total de sus campos y ubicación."
)
def modificar_equipo(id: str, equipo_in: EquipoUpdate):
    object_id = validate_object_id(id)
    collection = get_equipos_collection()

    try:
        equipo_actual = collection.find_one({"_id": object_id})
        if not equipo_actual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Equipo con identificador '{id}' no existe."
            )

        datos_actualizar = equipo_in.model_dump(exclude_unset=True)

        if not datos_actualizar:
            return serialize_doc(equipo_actual)

        # Validación de duplicidad si cambia código o serie
        condiciones_duplicado = []
        if "codigo" in datos_actualizar and datos_actualizar["codigo"] != equipo_actual.get("codigo"):
            condiciones_duplicado.append({"codigo": datos_actualizar["codigo"]})
        if "numero_serie" in datos_actualizar and datos_actualizar["numero_serie"] != equipo_actual.get("numero_serie"):
            condiciones_duplicado.append({"numero_serie": datos_actualizar["numero_serie"]})

        if condiciones_duplicado:
            colision = collection.find_one({
                "_id": {"$ne": object_id},
                "$or": condiciones_duplicado
            })
            if colision:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El nuevo código o número de serie ya está en uso por otro equipo."
                )

        # Si se actualiza la ubicación, se fusiona con la existente
        if "ubicacion" in datos_actualizar:
            ubicacion_actual = equipo_actual.get("ubicacion", {})
            ubicacion_actual.update(datos_actualizar["ubicacion"])
            datos_actualizar["ubicacion"] = ubicacion_actual

        collection.update_one(
            {"_id": object_id},
            {"$set": datos_actualizar}
        )

        equipo_actualizado = collection.find_one({"_id": object_id})
        return serialize_doc(equipo_actualizado)

    except HTTPException:
        raise
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al modificar el equipo: {str(err)}"
        )


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="5. Eliminar un equipo",
    description="Elimina permanentemente un equipo del inventario mediante su identificador."
)
def eliminar_equipo(id: str):
    object_id = validate_object_id(id)
    collection = get_equipos_collection()

    try:
        resultado = collection.delete_one({"_id": object_id})
        if resultado.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Equipo con identificador '{id}' no fue encontrado para eliminar."
            )
        return {
            "mensaje": f"Equipo con identificador '{id}' eliminado exitosamente.",
            "id": id,
            "eliminado": True
        }
    except HTTPException:
        raise
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el equipo: {str(err)}"
        )


@router.get(
    "/{id}/mantenimientos",
    response_model=List[MantenimientoResponse],
    summary="10. Consultar el historial de mantenimiento de un equipo",
    description="Devuelve la lista cronológica de todos los mantenimientos preventivos y correctivos realizados a un equipo."
)
def consultar_mantenimientos(id: str):
    object_id = validate_object_id(id)
    collection = get_equipos_collection()

    try:
        equipo = collection.find_one({"_id": object_id}, {"mantenimientos": 1})
        if not equipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Equipo con identificador '{id}' no existe."
            )
        mantenimientos = equipo.get("mantenimientos", [])
        return serialize_list(mantenimientos)
    except HTTPException:
        raise
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar el historial de mantenimiento: {str(err)}"
        )


@router.post(
    "/{id}/mantenimientos",
    response_model=MantenimientoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Extra: Registrar nuevo mantenimiento a un equipo",
    description="Agrega un registro de mantenimiento al arreglo 'mantenimientos' del equipo especificado."
)
def agregar_mantenimiento(id: str, mantenimiento_in: MantenimientoCreate):
    object_id = validate_object_id(id)
    collection = get_equipos_collection()

    try:
        equipo = collection.find_one({"_id": object_id})
        if not equipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Equipo con identificador '{id}' no existe."
            )

        nuevo_mantenimiento = mantenimiento_in.model_dump()
        collection.update_one(
            {"_id": object_id},
            {"$push": {"mantenimientos": nuevo_mantenimiento}}
        )

        return nuevo_mantenimiento
    except HTTPException:
        raise
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar el mantenimiento: {str(err)}"
        )
