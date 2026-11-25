def test_crud_completo_de_socio(client, crear_socio):
    socio = crear_socio(nombre="Ana", email="ana@mail.com")
    assert socio["activo"] is True

    assert client.get("/socios").json() == [socio]
    assert client.get(f"/socios/{socio['id']}").json() == socio

    r = client.patch(f"/socios/{socio['id']}", json={"activo": False})
    assert r.status_code == 200 and r.json()["activo"] is False

    assert client.delete(f"/socios/{socio['id']}").status_code == 204
    assert client.get(f"/socios/{socio['id']}").status_code == 404


def test_socio_inexistente_devuelve_404(client):
    assert client.get("/socios/999").status_code == 404
    assert client.patch("/socios/999", json={"nombre": "X"}).status_code == 404
    assert client.delete("/socios/999").status_code == 404
    assert client.get("/socios/999/prestamos").status_code == 404


def test_email_duplicado_al_crear_devuelve_409(client, crear_socio):
    crear_socio(email="repetido@mail.com")
    r = client.post("/socios", json={"nombre": "Otro", "email": "repetido@mail.com"})
    assert r.status_code == 409


def test_email_duplicado_al_modificar_devuelve_409(client, crear_socio):
    crear_socio(email="a@mail.com")
    b = crear_socio(email="b@mail.com")
    assert client.patch(f"/socios/{b['id']}", json={"email": "a@mail.com"}).status_code == 409
    assert client.patch(f"/socios/{b['id']}", json={"email": "b@mail.com"}).status_code == 200


def test_email_invalido_devuelve_422(client):
    assert client.post("/socios", json={"nombre": "X", "email": "no-es-mail"}).status_code == 422


def test_no_se_borra_socio_con_prestamos(client, crear_socio, crear_libro):
    socio, libro = crear_socio(), crear_libro()
    client.post("/prestamos", json={"socio_id": socio["id"], "libro_id": libro["id"]})
    assert client.delete(f"/socios/{socio['id']}").status_code == 409


def test_prestamos_del_socio_filtrados_por_activos(client, crear_socio, crear_libro):
    socio, libro = crear_socio(), crear_libro()
    p1 = client.post("/prestamos", json={"socio_id": socio["id"], "libro_id": libro["id"]}).json()
    p2 = client.post("/prestamos", json={"socio_id": socio["id"], "libro_id": libro["id"]}).json()
    client.post(f"/prestamos/{p1['id']}/devolucion")

    activos = client.get(f"/socios/{socio['id']}/prestamos?activos=true").json()
    assert [p["id"] for p in activos] == [p2["id"]]

    devueltos = client.get(f"/socios/{socio['id']}/prestamos?activos=false").json()
    assert [p["id"] for p in devueltos] == [p1["id"]]

    todos = client.get(f"/socios/{socio['id']}/prestamos").json()
    assert len(todos) == 2


def test_email_invalido_al_modificar_devuelve_422(client, crear_socio):
    socio = crear_socio()
    assert client.patch(f"/socios/{socio['id']}", json={"email": "sin arroba"}).status_code == 422
