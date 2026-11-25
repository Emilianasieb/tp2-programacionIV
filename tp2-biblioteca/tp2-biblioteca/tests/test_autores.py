def test_crud_completo_de_autor(client):
    r = client.post("/autores", json={"nombre": "Borges", "nacionalidad": "Argentina"})
    assert r.status_code == 201
    autor = r.json()
    assert autor["id"] is not None

    assert client.get("/autores").json() == [autor]
    assert client.get(f"/autores/{autor['id']}").json() == autor

    r = client.patch(f"/autores/{autor['id']}", json={"nacionalidad": "AR"})
    assert r.status_code == 200
    assert r.json()["nacionalidad"] == "AR"
    assert r.json()["nombre"] == "Borges"  # lo que no se manda no cambia

    assert client.delete(f"/autores/{autor['id']}").status_code == 204
    assert client.get(f"/autores/{autor['id']}").status_code == 404


def test_autor_inexistente_devuelve_404(client):
    assert client.get("/autores/999").status_code == 404
    assert client.patch("/autores/999", json={"nombre": "X"}).status_code == 404
    assert client.delete("/autores/999").status_code == 404


def test_autor_sin_nombre_devuelve_422(client):
    assert client.post("/autores", json={"nombre": ""}).status_code == 422
