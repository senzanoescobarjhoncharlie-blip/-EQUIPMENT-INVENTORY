from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from core.config import settings

_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    """Devuelve o inicializa la instancia global del cliente de MongoDB."""
    global _client
    if _client is None:
        _client = MongoClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connect=False  # Conexión lazy: no bloquea ni falla al importar en CI
        )
    return _client


def get_database() -> Database:
    """Devuelve la referencia a la base de datos configurada."""
    client = get_client()
    return client[settings.MONGODB_DB]


def get_equipos_collection() -> Collection:
    """Devuelve la colección principal de equipos."""
    db = get_database()
    return db[settings.MONGODB_COLLECTION]


def check_database_connection() -> bool:
    """Verifica si la conexión con MongoDB está activa."""
    try:
        client = get_client()
        client.admin.command("ping")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError):
        return False


def close_mongo_connection():
    """Cierra la conexión con el servidor de MongoDB."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
