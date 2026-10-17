import re
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Response, status
from pymongo.errors import PyMongoError

from core.database import get_equipos_collection
from schemas.equipo import (
    EquipoCreate,
    EquipoUpdate,
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
# 6. BUSCAR POR CÓDIGO, NÚMERO DE SERIE O MODELO (RUTA ESTÁTICA PREVIA A DINÁMICAS)
# ============================================================================
@router.get(
    "/buscar",
    response_model=List[EquipoResponse],
    summary="6. Buscar por código, número de serie o modelo",
    description="Permite buscar equipos por código, número de serie o modelo usando parámetros de consulta seguros."
)
def buscar_equipos(
    q: Optional[str] = Query(None, description="Término general a buscar en código, número de serie o modelo"),
    codigo: Optional[str] = Query(None, description="Búsqueda por coincidencia en código"),
    numero_serie: Optional[str] = Query(None, description="Búsqueda por coincidencia en número de serie"),
    modelo: Optional[str] = Query(None, description="Búsqueda por coincidencia en modelo comercial"),
    termino: Optional[str] = Query(None, description="Alias para el término general de búsqueda")
):
    collection = get_equipos_collection()

    condiciones = []

    # Búsqueda específica por criterios múltiples
    if codigo and codigo.strip():
        condiciones.append({"codigo": {"$regex": re.escape(codigo.strip()), "$options": "i"}})
    if numero_serie and numero_serie.strip():
        condiciones.append({"numero_serie": {"$regex": re.escape(numero_serie.strip()), "$options": "i"}})
    if modelo and modelo.strip():
        condiciones.append({"modelo": {"$regex": re.escape(modelo.strip()), "$options": "i"}})

    # Búsqueda general 'q' o 'termino'
    termino_general = q or termino
    if termino_general and termino_general.strip():
        patron = re.escape(termino_general.strip())
        condiciones.append({
            "$or": [
                {"codigo": {"$regex": patron, "$options": "i"}},
                {"numero_serie": {"$regex": patron, "$options": "i"}},
                {"modelo": {"$regex": patron, "$options": "i"}}
            ]
        })

    if not condiciones:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un criterio de búsqueda: 'q', 'codigo', 'numero_serie' o 'modelo'."
        )

    filtro = {"$and": condiciones} if len(condiciones) > 1 else condiciones[0]

    try:
        resultados = list(collection.find(filtro))
        return serialize_list(resultados)
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la consulta de búsqueda: {str(err)}"
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


# ============================================================================
# 4. MODIFICAR UN EQUIPO (PATCH / PUT)
# ============================================================================
@router.patch(
    "/{equipo_id}",
    response_model=EquipoResponse,
    summary="4. Modificar un equipo (actualización parcial)",
    description="Actualiza parcialmente los campos válidos de un equipo. Valida unicidad en caso de cambiar código o serie."
)
@router.put(
    "/{equipo_id}",
    response_model=EquipoResponse,
    summary="4b. Modificar un equipo (actualización total/parcial)",
    include_in_schema=False
)
def modificar_equipo(equipo_id: str, equipo_in: EquipoUpdate):
    object_id = validate_object_id(equipo_id)
    collection = get_equipos_collection()

    try:
        equipo_actual = collection.find_one({"_id": object_id})
        if not equipo_actual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Equipo con identificador '{equipo_id}' no existe."
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
                if colision.get("codigo") == datos_actualizar.get("codigo"):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"El código '{datos_actualizar['codigo']}' ya está en uso por otro equipo."
                    )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"El número de serie '{datos_actualizar['numero_serie']}' ya está en uso por otro equipo."
                )

        # Si se actualiza la ubicación, se fusiona con la existente
        if "ubicacion" in datos_actualizar and datos_actualizar["ubicacion"]:
            ubicacion_actual = equipo_actual.get("ubicacion", {})
            ubicacion_actual.update({k: v for k, v in datos_actualizar["ubicacion"].items() if v is not None})
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


# ============================================================================
# 5. ELIMINAR UN EQUIPO (204 NO CONTENT)
# ============================================================================
@router.delete(
    "/{equipo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="5. Eliminar un equipo",
    description="Elimina permanentemente un equipo del inventario mediante su identificador. Retorna 204 No Content sin cuerpo."
)
def eliminar_equipo(equipo_id: str):
    object_id = validate_object_id(equipo_id)
    collection = get_equipos_collection()

    try:
        resultado = collection.delete_one({"_id": object_id})
        if resultado.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Equipo con identificador '{equipo_id}' no fue encontrado para eliminar."
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except PyMongoError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el equipo: {str(err)}"
        )
