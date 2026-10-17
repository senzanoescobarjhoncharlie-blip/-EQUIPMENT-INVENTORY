from fastapi import APIRouter, HTTPException, status
from pymongo.errors import PyMongoError

from core.database import get_equipos_collection
from schemas.equipo import EquipoCreate, EquipoResponse
from utils.mongo import serialize_doc

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
