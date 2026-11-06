def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_producto_inexistente_da_404(client):
    assert client.get("/products/999").status_code == 404


def test_salida_resta_stock_sin_generar_solicitud(client):
    r = client.post("/products/1/movements", json={"tipo": "SALIDA", "cantidad": 5})
    assert r.status_code == 201
    datos = r.json()
    assert datos["stock_actual"] == 15
    assert datos["solicitud_generada"] is None


def test_salida_bajo_minimo_genera_solicitud(client):
    r = client.post("/products/1/movements", json={"tipo": "SALIDA", "cantidad": 13})
    solicitud = r.json()["solicitud_generada"]
    assert solicitud["cantidad"] == 13        # doble del mínimo (20) - stock (7)
    assert solicitud["estado"] == "PENDIENTE"


def test_no_duplica_solicitud_pendiente(client):
    client.post("/products/1/movements", json={"tipo": "SALIDA", "cantidad": 13})
    r = client.post("/products/1/movements", json={"tipo": "SALIDA", "cantidad": 1})
    assert r.json()["solicitud_generada"] is None
    assert len(client.get("/restock-requests").json()) == 1


def test_salida_mayor_al_stock_da_409_y_no_cambia_nada(client):
    r = client.post("/products/1/movements", json={"tipo": "SALIDA", "cantidad": 100})
    assert r.status_code == 409
    # Verifica el efecto secundario: el stock sigue igual
    assert client.get("/products/1").json()["stock"] == 20


def test_cantidad_cero_da_422(client):
    r = client.post("/products/1/movements", json={"tipo": "SALIDA", "cantidad": 0})
    assert r.status_code == 422


def test_aprobar_dos_veces_da_409(client):
    r = client.post("/products/1/movements", json={"tipo": "SALIDA", "cantidad": 13})
    solicitud_id = r.json()["solicitud_generada"]["id"]

    assert client.post(f"/restock-requests/{solicitud_id}/approve").status_code == 200
    assert client.post(f"/restock-requests/{solicitud_id}/approve").status_code == 409


def test_rechazar_sin_comentario_da_422(client):
    r = client.post("/products/1/movements", json={"tipo": "SALIDA", "cantidad": 13})
    solicitud_id = r.json()["solicitud_generada"]["id"]

    r = client.post(f"/restock-requests/{solicitud_id}/reject", json={"comentario": ""})
    assert r.status_code == 422

def test_generar_crea_solicitudes_faltantes(client):
    r = client.post("/restock-requests/generate")
    assert r.status_code == 200
    creadas = r.json()
    assert len(creadas) == 1               # solo la regleta (7 de 10)
    assert creadas[0]["producto_id"] == 2
    assert creadas[0]["cantidad"] == 13    # 20 - 7


def test_generar_es_idempotente(client):
    client.post("/restock-requests/generate")
    r = client.post("/restock-requests/generate")
    assert r.json() == []                  # la segunda vez no crea nada