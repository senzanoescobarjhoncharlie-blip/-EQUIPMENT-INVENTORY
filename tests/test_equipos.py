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
