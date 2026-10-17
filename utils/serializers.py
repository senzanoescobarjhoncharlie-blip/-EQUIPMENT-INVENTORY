from typing import Any, Dict, List, Optional
from bson import ObjectId
from datetime import date, datetime


def serialize_value(val: Any) -> Any:
    """Convierte tipos de datos de MongoDB a formatos serializables en JSON."""
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
    """Convierte un documento de MongoDB a diccionario serializable."""
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
    return [serialize_doc(doc) for doc in docs if doc]
