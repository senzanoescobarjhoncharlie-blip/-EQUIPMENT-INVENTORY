from bson import ObjectId

SAMPLE_EQUIPO = {
    "codigo": "EQ-PRB-001",
    "tipo": "Laptop",
    "marca": "Dell",
    "modelo": "Latitude 5420",
    "numero_serie": "SN-DL5420-001",
    "fecha_adquisicion": "2024-03-01",
    "estado": "disponible",
    "caracteristicas": ["16GB RAM", "512GB SSD", "Intel Core i7"],
    "ubicacion": {
        "edificio": "Edificio Central",
        "ambiente": "Laboratorio 1",
        "responsable": "Lic. Roberto Pérez"
    },
    "mantenimientos": []
}


def test_raiz_y_salud(client):
    """Verifica que la API inicial arranca y responde correctamente."""
    res_raiz = client.get("/")
    assert res_raiz.status_code == 200
    assert "aplicacion" in res_raiz.json()

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"


# ============================================================================
# 1. PRUEBAS DE REGISTRO (POST /api/v1/equipos)
# ============================================================================
def test_registrar_equipo_valido(client):
    """Verifica el registro exitoso de un equipo informático."""
    response = client.post("/api/v1/equipos", json=SAMPLE_EQUIPO)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["codigo"] == "EQ-PRB-001"
    assert data["numero_serie"] == "SN-DL5420-001"
    assert data["estado"] == "disponible"
    assert data["ubicacion"]["responsable"] == "Lic. Roberto Pérez"


def test_registrar_equipo_invalido_faltan_campos(client):
    """Verifica que campos faltantes o vacíos generen 422 Unprocessable Entity."""
    invalido = {"codigo": "   "}
    response = client.post("/api/v1/equipos", json=invalido)
    assert response.status_code == 422


def test_registrar_equipo_duplicado_codigo(client):
    """Verifica error 409 Conflict cuando el código ya existe."""
    client.post("/api/v1/equipos", json=SAMPLE_EQUIPO)

    duplicado = dict(SAMPLE_EQUIPO)
    duplicado["numero_serie"] = "SN-OTRO-999"
    response = client.post("/api/v1/equipos", json=duplicado)
    assert response.status_code == 409
    assert "código" in response.json()["detail"].lower()


def test_registrar_equipo_duplicado_numero_serie(client):
    """Verifica error 409 Conflict cuando el número de serie ya existe."""
    client.post("/api/v1/equipos", json=SAMPLE_EQUIPO)

    duplicado = dict(SAMPLE_EQUIPO)
    duplicado["codigo"] = "EQ-OTRO-999"
    response = client.post("/api/v1/equipos", json=duplicado)
    assert response.status_code == 409
    assert "serie" in response.json()["detail"].lower()


# ============================================================================
# 2. PRUEBAS DE LISTADO Y PAGINACIÓN (GET /api/v1/equipos)
# ============================================================================
def test_listar_equipos_vacio(client):
    """Verifica respuesta adecuada cuando no hay equipos registrados."""
    response = client.get("/api/v1/equipos")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["equipos"] == []


def test_listar_equipos_con_paginacion(client):
    """Verifica funcionamiento de paginación con skip y limit."""
    for i in range(5):
        eq = dict(SAMPLE_EQUIPO)
        eq["codigo"] = f"EQ-PAG-{i}"
        eq["numero_serie"] = f"SN-PAG-{i}"
        client.post("/api/v1/equipos", json=eq)

    response = client.get("/api/v1/equipos?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["equipos"]) == 2


# ============================================================================
# 3. PRUEBAS DE CONSULTA POR IDENTIFICADOR (GET /api/v1/equipos/{id})
# ============================================================================
def test_consultar_equipo_por_id_valido(client):
    """Verifica consulta exitosa de un equipo existente mediante su ID."""
    creado = client.post("/api/v1/equipos", json=SAMPLE_EQUIPO).json()
    equipo_id = creado["id"]

    response = client.get(f"/api/v1/equipos/{equipo_id}")
    assert response.status_code == 200
    assert response.json()["id"] == equipo_id
    assert response.json()["codigo"] == SAMPLE_EQUIPO["codigo"]


def test_consultar_equipo_inexistente(client):
    """Verifica error 404 Not Found para un ObjectId válido pero inexistente."""
    fake_id = str(ObjectId())
    response = client.get(f"/api/v1/equipos/{fake_id}")
    assert response.status_code == 404


def test_consultar_equipo_id_invalido(client):
    """Verifica error 400 Bad Request cuando el identificador no es ObjectId."""
    response = client.get("/api/v1/equipos/id-invalido-123")
    assert response.status_code == 400
