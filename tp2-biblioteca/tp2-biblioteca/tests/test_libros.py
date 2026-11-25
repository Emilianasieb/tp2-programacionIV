def test_crud_completo_de_libro(client, crear_libro):
    libro = crear_libro(titulo="Ficciones", isbn="111")
    assert libro["autores"] == []

    assert client.get(f"/libros/{libro['id']}").json()["titulo"] == "Ficciones"
    r = client.patch(f"/libros/{libro['id']}", json={"stock": 10})
    assert r.status_code == 200 and r.json()["stock"] == 10

    assert client.delete(f"/libros/{libro['id']}").status_code == 204
    assert client.get(f"/libros/{libro['id']}").status_code == 404


def test_libro_inexistente_devuelve_404(client):
    assert client.get("/libros/999").status_code == 404
    assert client.patch("/libros/999", json={"stock": 1}).status_code == 404
    assert client.delete("/libros/999").status_code == 404


def test_isbn_duplicado_al_crear_devuelve_409(client, crear_libro):
    crear_libro(isbn="123")
    r = client.post("/libros", json={"titulo": "Otro", "isbn": "123", "stock": 1})
    assert r.status_code == 409


def test_isbn_duplicado_al_modificar_devuelve_409(client, crear_libro):
    crear_libro(isbn="AAA")
    b = crear_libro(isbn="BBB")
    assert client.patch(f"/libros/{b['id']}", json={"isbn": "AAA"}).status_code == 409
    # mandar su propio ISBN no es duplicado
    assert client.patch(f"/libros/{b['id']}", json={"isbn": "BBB"}).status_code == 200


def test_stock_negativo_devuelve_422(client):
    r = client.post("/libros", json={"titulo": "X", "isbn": "1", "stock": -1})
    assert r.status_code == 422


def test_filtro_disponibles(client, crear_libro):
    con_stock = crear_libro(stock=2)
    sin_stock = crear_libro(stock=0)

    ids_disponibles = [l["id"] for l in client.get("/libros?disponibles=true").json()]
    assert ids_disponibles == [con_stock["id"]]

    ids_sin_stock = [l["id"] for l in client.get("/libros?disponibles=false").json()]
    assert ids_sin_stock == [sin_stock["id"]]

    assert len(client.get("/libros").json()) == 2


def test_asociar_autor_a_libro(client, crear_libro):
    libro = crear_libro()
    autor = client.post("/autores", json={"nombre": "Cortázar"}).json()

    r = client.post(f"/libros/{libro['id']}/autores/{autor['id']}")
    assert r.status_code == 201
    assert r.json()["autores"] == [autor]
    # la respuesta del GET también incluye los autores
    assert client.get(f"/libros/{libro['id']}").json()["autores"] == [autor]


def test_libro_con_varios_autores_y_autor_con_varios_libros(client, crear_libro):
    l1, l2 = crear_libro(), crear_libro()
    a1 = client.post("/autores", json={"nombre": "A1"}).json()
    a2 = client.post("/autores", json={"nombre": "A2"}).json()
    client.post(f"/libros/{l1['id']}/autores/{a1['id']}")
    client.post(f"/libros/{l1['id']}/autores/{a2['id']}")
    client.post(f"/libros/{l2['id']}/autores/{a1['id']}")

    assert len(client.get(f"/libros/{l1['id']}").json()["autores"]) == 2
    assert len(client.get(f"/libros/{l2['id']}").json()["autores"]) == 1


def test_asociar_autor_dos_veces_devuelve_409(client, crear_libro):
    libro = crear_libro()
    autor = client.post("/autores", json={"nombre": "X"}).json()
    client.post(f"/libros/{libro['id']}/autores/{autor['id']}")
    assert client.post(f"/libros/{libro['id']}/autores/{autor['id']}").status_code == 409


def test_asociar_con_libro_o_autor_inexistente_devuelve_404(client, crear_libro):
    libro = crear_libro()
    autor = client.post("/autores", json={"nombre": "X"}).json()
    assert client.post(f"/libros/999/autores/{autor['id']}").status_code == 404
    assert client.post(f"/libros/{libro['id']}/autores/999").status_code == 404


def test_borrar_autor_lo_quita_de_sus_libros(client, crear_libro):
    libro = crear_libro()
    autor = client.post("/autores", json={"nombre": "X"}).json()
    client.post(f"/libros/{libro['id']}/autores/{autor['id']}")

    assert client.delete(f"/autores/{autor['id']}").status_code == 204
    assert client.get(f"/libros/{libro['id']}").json()["autores"] == []


def test_no_se_borra_libro_con_prestamos(client, crear_libro, crear_socio):
    libro = crear_libro()
    socio = crear_socio()
    client.post("/prestamos", json={"socio_id": socio["id"], "libro_id": libro["id"]})
    assert client.delete(f"/libros/{libro['id']}").status_code == 409
