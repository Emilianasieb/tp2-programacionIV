def test_raiz(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "/docs" in r.json()["mensaje"]
