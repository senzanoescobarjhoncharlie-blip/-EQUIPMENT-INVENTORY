from fastapi import APIRouter, HTTPException, status
from pymongo.errors import PyMongoError

from core.database import get_equipos_collection
from schemas.equipo import EquipoCreate, EquipoResponse
from utils.serializers import serialize_doc

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
