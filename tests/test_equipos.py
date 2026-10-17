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


# ============================================================================
# 4. PRUEBAS DE MODIFICACIÓN PARCIAL (PATCH /api/v1/equipos/{id})
# ============================================================================
def test_modificar_equipo_parcial(client):
    """Verifica actualización parcial mediante PATCH."""
    creado = client.post("/api/v1/equipos", json=SAMPLE_EQUIPO).json()
    equipo_id = creado["id"]

    cambios = {
        "modelo": "Latitude 5430",
        "estado": "en_mantenimiento"
    }
    response = client.patch(f"/api/v1/equipos/{equipo_id}", json=cambios)
    assert response.status_code == 200
    data = response.json()
    assert data["modelo"] == "Latitude 5430"
    assert data["estado"] == "en_mantenimiento"
    assert data["codigo"] == SAMPLE_EQUIPO["codigo"]


def test_modificar_equipo_conflicto_codigo(client):
    """Verifica error 409 si la actualización colisiona con el código de otro equipo."""
    eq1 = client.post("/api/v1/equipos", json=SAMPLE_EQUIPO).json()

    eq2_data = dict(SAMPLE_EQUIPO)
    eq2_data["codigo"] = "EQ-OTRO-002"
    eq2_data["numero_serie"] = "SN-OTRO-002"
    eq2 = client.post("/api/v1/equipos", json=eq2_data).json()

    response = client.patch(f"/api/v1/equipos/{eq2['id']}", json={"codigo": SAMPLE_EQUIPO["codigo"]})
    assert response.status_code == 409


# ============================================================================
# 5. PRUEBAS DE ELIMINACIÓN (DELETE /api/v1/equipos/{id})
# ============================================================================
def test_eliminar_equipo_exitoso(client):
    """Verifica eliminación exitosa retornando 204 No Content sin cuerpo."""
    creado = client.post("/api/v1/equipos", json=SAMPLE_EQUIPO).json()
    equipo_id = creado["id"]

    response = client.delete(f"/api/v1/equipos/{equipo_id}")
    assert response.status_code == 204
    assert response.content == b""

    # Verificar que ya no existe
    assert client.get(f"/api/v1/equipos/{equipo_id}").status_code == 404


def test_eliminar_equipo_inexistente(client):
    """Verifica 404 al intentar eliminar un equipo que no existe."""
    fake_id = str(ObjectId())
    response = client.delete(f"/api/v1/equipos/{fake_id}")
    assert response.status_code == 404


# ============================================================================
# 6. PRUEBAS DE BÚSQUEDA (GET /api/v1/equipos/buscar)
# ============================================================================
def test_buscar_equipos_por_criterios(client):
    """Verifica búsqueda por código, serie o modelo."""
    client.post("/api/v1/equipos", json=SAMPLE_EQUIPO)

    # Por término general 'q'
    res_q = client.get("/api/v1/equipos/buscar?q=DL5420")
    assert res_q.status_code == 200
    assert len(res_q.json()) == 1

    # Por código específico
    res_cod = client.get("/api/v1/equipos/buscar?codigo=EQ-PRB-001")
    assert res_cod.status_code == 200
    assert len(res_cod.json()) == 1

    # Por serie específica
    res_ser = client.get("/api/v1/equipos/buscar?numero_serie=SN-DL5420-001")
    assert res_ser.status_code == 200
    assert len(res_ser.json()) == 1

    # Por modelo
    res_mod = client.get("/api/v1/equipos/buscar?modelo=Latitude")
    assert res_mod.status_code == 200
    assert len(res_mod.json()) == 1


def test_buscar_equipos_sin_criterios(client):
    """Verifica 400 Bad Request si no se envía ningún parámetro de búsqueda."""
    response = client.get("/api/v1/equipos/buscar")
    assert response.status_code == 400


# ============================================================================
# 7. PRUEBAS DE FILTRO POR TIPO (GET /api/v1/equipos/filtrar/tipo)
# ============================================================================
def test_filtrar_por_tipo(client):
    """Verifica filtrado de equipos por categoría o tipo."""
    client.post("/api/v1/equipos", json=SAMPLE_EQUIPO)

    res_tipo_query = client.get("/api/v1/equipos/filtrar/tipo?tipo=Laptop")
    assert res_tipo_query.status_code == 200
    assert len(res_tipo_query.json()) == 1

    res_tipo_path = client.get("/api/v1/equipos/filtrar/tipo/Laptop")
    assert res_tipo_path.status_code == 200
    assert len(res_tipo_path.json()) == 1


# ============================================================================
# 8. PRUEBAS DE FILTRO POR MARCA (GET /api/v1/equipos/filtrar/marca)
# ============================================================================
def test_filtrar_por_marca(client):
    """Verifica filtrado de equipos por marca del fabricante."""
    client.post("/api/v1/equipos", json=SAMPLE_EQUIPO)

    res_marca_query = client.get("/api/v1/equipos/filtrar/marca?marca=Dell")
    assert res_marca_query.status_code == 200
    assert len(res_marca_query.json()) == 1

    res_marca_path = client.get("/api/v1/equipos/filtrar/marca/Dell")
    assert res_marca_path.status_code == 200
    assert len(res_marca_path.json()) == 1


# ============================================================================
# 9. PRUEBAS DE FILTRO POR ESTADO (GET /api/v1/equipos/filtrar/estado)
# ============================================================================
def test_filtrar_por_estado(client):
    """Verifica filtrado de equipos por su situación o estado actual."""
    client.post("/api/v1/equipos", json=SAMPLE_EQUIPO)

    res_estado_query = client.get("/api/v1/equipos/filtrar/estado?estado=disponible")
    assert res_estado_query.status_code == 200
    assert len(res_estado_query.json()) == 1

    res_estado_path = client.get("/api/v1/equipos/filtrar/estado/disponible")
    assert res_estado_path.status_code == 200
    assert len(res_estado_path.json()) == 1


# ============================================================================
# 10. PRUEBAS DE HISTORIAL DE MANTENIMIENTO
# ============================================================================
def test_historial_mantenimiento_vacio_y_con_registros(client):
    """Verifica historial de mantenimiento vacío y tras agregar registros."""
    creado = client.post("/api/v1/equipos", json=SAMPLE_EQUIPO).json()
    equipo_id = creado["id"]

    # Historial inicial vacío
    res_hist = client.get(f"/api/v1/equipos/{equipo_id}/mantenimientos")
    assert res_hist.status_code == 200
    assert res_hist.json() == []

    # Registrar un mantenimiento
    mantenimiento = {
        "fecha": "2025-02-10",
        "tipo": "Preventivo",
        "descripcion": "Limpieza general y mantenimiento térmico",
        "tecnico": "Ing. Carlos Mendoza",
        "costo": 45.0
    }
    res_add = client.post(f"/api/v1/equipos/{equipo_id}/mantenimientos", json=mantenimiento)
    assert res_add.status_code == 201

    # Consultar nuevamente
    res_hist_updated = client.get(f"/api/v1/equipos/{equipo_id}/mantenimientos")
    assert res_hist_updated.status_code == 200
    assert len(res_hist_updated.json()) == 1
    assert res_hist_updated.json()[0]["tecnico"] == "Ing. Carlos Mendoza"


def test_historial_mantenimiento_equipo_inexistente(client):
    """Verifica error 404 al consultar historial de un equipo inexistente."""
    fake_id = str(ObjectId())
    response = client.get(f"/api/v1/equipos/{fake_id}/mantenimientos")
    assert response.status_code == 404
