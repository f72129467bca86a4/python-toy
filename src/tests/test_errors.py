from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.testclient import TestClient
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from python_toy.server.infra.error.problem import MEDIA_TYPE


def test_validation_error_problem_details(client: TestClient):
    # name 필드 최소 길이 위반
    r = client.post("/v1/pets", json={"name": "", "tags": []})
    assert r.status_code == 400
    assert r.headers["content-type"].startswith(MEDIA_TYPE)
    data = r.json()
    assert data["type"].endswith("/error/validation") or data["type"].startswith("//localhost/error/validation")
    assert data["status"] == 400
    assert "errors" in data
    # bytes normalization 은 여기서 다루지 않음(별도 필요 시 추가)


def test_http_exception_to_problem_details(client: TestClient):
    # 존재하지 않는 pet 조회 -> 404
    r = client.get("/v1/pets/unknown")
    assert r.status_code == HTTP_404_NOT_FOUND
    data = r.json()
    assert data["status"] == 404
    assert "not found" in data["detail"]


def test_unhandled_exception_catch_all(client: TestClient):
    # 테스트 전용 라우터 동적 주입 (서비스 코드 오염 방지)
    router = APIRouter()

    @router.get("/boom")
    async def boom() -> None:
        raise RuntimeError("boom")  # noqa: EM101

    # Request time router 주입
    client.app.include_router(router)

    r = client.get("/boom")
    assert r.status_code == 500
    data = r.json()
    assert data["status"] == 500
    assert data["detail"] == "Internal Server Error"


def test_custom_http_exception(client: TestClient):
    router = APIRouter()

    @router.get("/custom")
    async def custom() -> None:  # noqa: ANN201
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="bad_thing")

    client.app.include_router(router)

    r = client.get("/custom")
    assert r.status_code == 400
    data = r.json()
    assert data["detail"] == "bad_thing"
    assert data["status"] == 400
