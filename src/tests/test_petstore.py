from __future__ import annotations

from fastapi.testclient import TestClient


def test_pet_crud(client: TestClient):
    r = client.post("/v1/pets", json={"name": "toto", "tags": ["dog"]})
    assert r.status_code == 201, r.text
    pet = r.json()
    assert pet["id"] == "1"
    assert pet["name"] == "toto"
    assert pet["tags"] == ["dog"]

    r = client.get("/v1/pets")
    assert r.status_code == 200
    pets = r.json()
    assert len(pets["items"]) >= 1

    r = client.get("/v1/pets/1")
    assert r.status_code == 200
    assert r.json()["name"] == "toto"

    r = client.patch("/v1/pets/1", json={"name": "tata"})
    assert r.status_code == 200
    assert r.json()["name"] == "tata"

    r = client.delete("/v1/pets/1")
    assert r.status_code == 200

    r = client.get("/v1/pets/1")
    assert r.status_code == 404
