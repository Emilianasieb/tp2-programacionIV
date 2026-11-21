"""Un test de caso feliz y uno de error por cada regla de negocio."""
from datetime import date, timedelta

from app.services.prestamos import calcular_multa


def prestar(client, socio_id, libro_id, **extra):
    return client.post("/prestamos", json={"socio_id": socio_id, "libro_id": libro_id, **extra})


# ---------- Regla 1: máximo 3 préstamos activos (409) ----------

def test_r1_socio_puede_tener_hasta_3_prestamos(client, crear_socio, crear_libro):
    socio, libro = crear_socio(), crear_libro(stock=10)
    for _ in range(3):
        assert prestar(client, socio["id"], libro["id"]).status_code == 201


def test_r1_cuarto_prestamo_activo_devuelve_409(client, crear_socio, crear_libro):
    socio, libro = crear_socio(), crear_libro(stock=10)
    for _ in range(3):
        prestar(client, socio["id"], libro["id"])
    r = prestar(client, socio["id"], libro["id"])
    assert r.status_code == 409
    # el stock no se tocó en el intento fallido
    assert client.get(f"/libros/{libro['id']}").json()["stock"] == 7


def test_r1_al_devolver_se_libera_un_lugar(client, crear_socio, crear_libro):
    socio, libro = crear_socio(), crear_libro(stock=10)
    ids = [prestar(client, socio["id"], libro["id"]).json()["id"] for _ in range(3)]
    client.post(f"/prestamos/{ids[0]}/devolucion")
    assert prestar(client, socio["id"], libro["id"]).status_code == 201


# ---------- Regla 2: stock (409) y descuento ----------

def test_r2_prestar_descuenta_stock(client, crear_socio, crear_libro):
    socio, libro = crear_socio(), crear_libro(stock=2)
    assert prestar(client, socio["id"], libro["id"]).status_code == 201
    assert client.get(f"/libros/{libro['id']}").json()["stock"] == 1


def test_r2_libro_sin_stock_devuelve_409(client, crear_socio, crear_libro):
    socio, libro = crear_socio(), crear_libro(stock=0)
    assert prestar(client, socio["id"], libro["id"]).status_code == 409


def test_r2_ultimo_ejemplar_deja_el_libro_no_disponible(client, crear_socio, crear_libro):
    s1, s2, libro = crear_socio(), crear_socio(), crear_libro(stock=1)
    assert prestar(client, s1["id"], libro["id"]).status_code == 201
    assert client.get("/libros?disponibles=true").json() == []
    assert prestar(client, s2["id"], libro["id"]).status_code == 409


# ---------- Regla 3: socio inactivo (403) ----------

def test_r3_socio_activo_puede_pedir(client, crear_socio, crear_libro):
    socio, libro = crear_socio(activo=True), crear_libro()
    assert prestar(client, socio["id"], libro["id"]).status_code == 201


def test_r3_socio_inactivo_devuelve_403(client, crear_socio, crear_libro):
    socio, libro = crear_socio(activo=False), crear_libro(stock=1)
    r = prestar(client, socio["id"], libro["id"])
    assert r.status_code == 403
    assert client.get(f"/libros/{libro['id']}").json()["stock"] == 1


# ---------- Regla 4: vencimiento a 14 días ----------

def test_r4_vencimiento_es_14_dias_despues(client, crear_socio, crear_libro):
    socio, libro = crear_socio(), crear_libro()
    r = prestar(client, socio["id"], libro["id"], fecha_prestamo="2026-11-01")
    assert r.json()["fecha_prestamo"] == "2026-11-01"
    assert r.json()["fecha_vencimiento"] == "2026-11-15"
    assert r.json()["fecha_devolucion"] is None
    assert r.json()["multa"] == 0


def test_r4_sin_fecha_usa_hoy(client, crear_socio, crear_libro):
    socio, libro = crear_socio(), crear_libro()
    r = prestar(client, socio["id"], libro["id"]).json()
    hoy = date.today()
    assert r["fecha_prestamo"] == hoy.isoformat()
    assert r["fecha_vencimiento"] == (hoy + timedelta(days=14)).isoformat()


# ---------- Regla 5: devolución repone stock y calcula multa ----------

def test_r5_devolucion_a_tiempo_sin_multa_y_repone_stock(client, crear_socio, crear_libro):
    socio, libro = crear_socio(), crear_libro(stock=1)
    p = prestar(client, socio["id"], libro["id"], fecha_prestamo="2026-11-01").json()
    r = client.post(f"/prestamos/{p['id']}/devolucion", json={"fecha_devolucion": "2026-11-15"})
    assert r.status_code == 200
    assert r.json()["multa"] == 0
    assert r.json()["fecha_devolucion"] == "2026-11-15"
    assert client.get(f"/libros/{libro['id']}").json()["stock"] == 1


def test_r5_devolucion_con_atraso_cobra_100_por_dia(client, crear_socio, crear_libro):
    socio, libro = crear_socio(), crear_libro()
    p = prestar(client, socio["id"], libro["id"], fecha_prestamo="2026-11-01").json()
    # vence el 15/11, se devuelve el 20/11 -> 5 días de atraso
    r = client.post(f"/prestamos/{p['id']}/devolucion", json={"fecha_devolucion": "2026-11-20"})
    assert r.json()["multa"] == 500


def test_r5_devolucion_sin_body_usa_hoy(client, crear_socio, crear_libro):
    socio, libro = crear_socio(), crear_libro()
    p = prestar(client, socio["id"], libro["id"]).json()
    r = client.post(f"/prestamos/{p['id']}/devolucion")
    assert r.status_code == 200
    assert r.json()["fecha_devolucion"] == date.today().isoformat()
    assert r.json()["multa"] == 0


def test_r5_calcular_multa_unitario():
    venc = date(2026, 11, 15)
    assert calcular_multa(venc, date(2026, 11, 10)) == 0   # antes
    assert calcular_multa(venc, date(2026, 11, 15)) == 0   # justo el día
    assert calcular_multa(venc, date(2026, 11, 16)) == 100  # 1 día tarde


def test_r5_devolucion_anterior_al_prestamo_devuelve_409(client, crear_socio, crear_libro):
    socio, libro = crear_socio(), crear_libro()
    p = prestar(client, socio["id"], libro["id"], fecha_prestamo="2026-11-10").json()
    r = client.post(f"/prestamos/{p['id']}/devolucion", json={"fecha_devolucion": "2026-11-01"})
    assert r.status_code == 409


# ---------- Regla 6: no se devuelve dos veces (409) ----------

def test_r6_devolver_dos_veces_devuelve_409(client, crear_socio, crear_libro):
    socio, libro = crear_socio(), crear_libro(stock=1)
    p = prestar(client, socio["id"], libro["id"]).json()
    assert client.post(f"/prestamos/{p['id']}/devolucion").status_code == 200
    assert client.post(f"/prestamos/{p['id']}/devolucion").status_code == 409
    # el stock se repuso una sola vez
    assert client.get(f"/libros/{libro['id']}").json()["stock"] == 1


# ---------- Regla 7: recursos inexistentes (404) ----------

def test_r7_prestamo_con_socio_inexistente(client, crear_libro):
    assert prestar(client, 999, crear_libro()["id"]).status_code == 404


def test_r7_prestamo_con_libro_inexistente(client, crear_socio):
    assert prestar(client, crear_socio()["id"], 999).status_code == 404


def test_r7_devolver_prestamo_inexistente(client):
    assert client.post("/prestamos/999/devolucion").status_code == 404


def test_r7_obtener_prestamo(client, crear_socio, crear_libro):
    p = prestar(client, crear_socio()["id"], crear_libro()["id"]).json()
    assert client.get(f"/prestamos/{p['id']}").json() == p
    assert client.get("/prestamos").json() == [p]
    assert client.get("/prestamos/999").status_code == 404
