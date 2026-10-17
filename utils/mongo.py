from typing import Any, Dict, List, Optional
from bson import ObjectId
from datetime import date, datetime
from fastapi import HTTPException, status


def validate_object_id(id_str: str) -> ObjectId:
    """
    Valida y convierte una cadena a ObjectId de MongoDB.
    Lanza HTTPException con código 400 Bad Request si el formato no es válido.
    """
    if not ObjectId.is_valid(id_str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El identificador '{id_str}' no es un ObjectId válido de MongoDB."
        )
    return ObjectId(id_str)


def serialize_value(val: Any) -> Any:
    """Convierte tipos de datos de MongoDB a formatos serializables en JSON estándar."""
    if isinstance(val, ObjectId):
        return str(val)
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    if isinstance(val, dict):
        return serialize_doc(val)
    if isinstance(val, list):
        return [serialize_value(item) for item in val]
    return val


def serialize_doc(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Convierte un documento de MongoDB a diccionario serializable en JSON.
    Asigna tanto 'id' como '_id' en formato string para compatibilidad de esquemas.
    """
    if not doc:
        return None
    serialized = {}
    for key, value in doc.items():
        if key == "_id" and isinstance(value, ObjectId):
            serialized["id"] = str(value)
            serialized["_id"] = str(value)
        else:
            serialized[key] = serialize_value(value)
    return serialized


def serialize_list(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Serializa una lista de documentos de MongoDB."""
    return [serialize_doc(doc) for doc in docs if doc is not None]


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Recurso no encontrado"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictException(HTTPException):
    def __init__(self, detail: str = "Conflicto con recurso existente"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class DatabaseConnectionException(HTTPException):
    def __init__(self, detail: str = "Error al conectar con la base de datos MongoDB"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)
