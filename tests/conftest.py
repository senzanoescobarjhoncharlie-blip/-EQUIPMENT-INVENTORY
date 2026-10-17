import pytest
import mongomock
from fastapi.testclient import TestClient
from main import app
import core.database as db_module


@pytest.fixture(scope="function")
def mock_mongo():
    """Provee un cliente simulado en memoria con mongomock para aislar las pruebas."""
    mock_client = mongomock.MongoClient()
    orig_get_client = db_module.get_client
    orig_get_db = db_module.get_database
    orig_get_coll = db_module.get_equipos_collection
    orig_check_conn = db_module.check_database_connection

    mock_db = mock_client["inventario_equipos_test"]
    mock_collection = mock_db["equipos"]

    db_module.get_client = lambda: mock_client
    db_module.get_database = lambda: mock_db
    db_module.get_equipos_collection = lambda: mock_collection
    db_module.check_database_connection = lambda: True

    yield mock_collection

    # Limpieza
    mock_collection.drop()
    db_module.get_client = orig_get_client
    db_module.get_database = orig_get_db
    db_module.get_equipos_collection = orig_get_coll
    db_module.check_database_connection = orig_check_conn


@pytest.fixture(scope="function")
def client(mock_mongo):
    """Cliente de pruebas de FastAPI sobre la base simulada."""
    with TestClient(app) as test_client:
        yield test_client
