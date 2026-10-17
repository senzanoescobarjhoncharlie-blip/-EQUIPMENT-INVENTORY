def test_raiz_y_salud(client):
    """Verifica que la API inicial arranca y responde correctamente."""
    res_raiz = client.get("/")
    assert res_raiz.status_code == 200
    assert "aplicacion" in res_raiz.json()

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"
