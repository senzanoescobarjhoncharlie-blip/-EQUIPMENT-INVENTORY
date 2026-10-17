from bson import ObjectId
from fastapi import HTTPException, status


def validate_object_id(id_str: str) -> ObjectId:
    """Valida y convierte una cadena a ObjectId de MongoDB o lanza HTTP 400."""
    if not ObjectId.is_valid(id_str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El identificador '{id_str}' no es un ObjectId válido de MongoDB."
        )
    return ObjectId(id_str)


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Recurso no encontrado"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictException(HTTPException):
    def __init__(self, detail: str = "Conflicto con recurso existente"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class DatabaseConnectionException(HTTPException):
    def __init__(self, detail: str = "Error al conectar con la base de datos MongoDB"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)
