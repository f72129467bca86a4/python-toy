from __future__ import annotations

from fastapi.testclient import TestClient


def test_root_meta(client: TestClient):
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["service"] == "python-toy"
