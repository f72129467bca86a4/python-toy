"""Tests for exception hierarchy and error handling."""

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from python_toy.server.infra.error import (
    ConflictException,
    ConcurrentModificationException,
    DuplicateEntityException,
)
from python_toy.server.infra.error import middleware as error_middleware


class TestExceptionHttpHandling:
    """Test HTTP error handling for custom exceptions."""

    def test_duplicate_entity_exception_http_response(self) -> None:
        """Test DuplicateEntityException HTTP response format."""
        app = FastAPI()
        error_middleware.setup(app)
        test_router = APIRouter()

        @test_router.post("/test/duplicate-entity")
        async def raise_duplicate_entity():
            entity_type = "User"
            field = "email"
            value = "test@example.com"
            raise DuplicateEntityException(entity_type, field, value)

        app.include_router(test_router)

        with TestClient(app) as client:
            response = client.post("/test/duplicate-entity")

            assert response.status_code == 409
            data = response.json()
            assert data["type"] == "//localhost/error/duplicate-entity"
            assert data["title"] == "Duplicate Entity"
            assert data["status"] == 409
            assert "User with email 'test@example.com' already exists" in data["detail"]
            assert data["entity_type"] == "User"
            assert data["field"] == "email"
            assert data["value"] == "test@example.com"

    def test_concurrent_modification_exception_http_response(self) -> None:
        """Test ConcurrentModificationException HTTP response format."""
        app = FastAPI()
        error_middleware.setup(app)
        test_router = APIRouter()

        @test_router.put("/test/concurrent-modification")
        async def raise_concurrent_modification():
            entity_type = "Pet"
            entity_id = "pet-123"
            raise ConcurrentModificationException(entity_type, entity_id)

        app.include_router(test_router)

        with TestClient(app) as client:
            response = client.put("/test/concurrent-modification")

            assert response.status_code == 409
            data = response.json()
            assert data["type"] == "//localhost/error/concurrent-modification"
            assert data["title"] == "Concurrent Modification Conflict"
            assert data["status"] == 409
            assert "Pet 'pet-123' was modified by another process" in data["detail"]
            assert data["entity_type"] == "Pet"
            assert data["entity_id"] == "pet-123"

    def test_generic_conflict_exception_http_response(self) -> None:
        """Test generic ConflictException HTTP response format."""
        app = FastAPI()
        error_middleware.setup(app)
        test_router = APIRouter()

        @test_router.patch("/test/generic-conflict")
        async def raise_generic_conflict():
            message = "Generic conflict occurred"
            raise ConflictException(message)

        app.include_router(test_router)

        with TestClient(app) as client:
            response = client.patch("/test/generic-conflict")

            assert response.status_code == 409
            data = response.json()
            assert data["type"] == "//localhost/error/conflict"
            assert data["title"] == "Conflict"
            assert data["status"] == 409
            assert "Generic conflict occurred" in data["detail"]

    def test_problem_details_content_type(self) -> None:
        """Test that exceptions return proper Problem Details content type."""
        app = FastAPI()
        error_middleware.setup(app)
        test_router = APIRouter()

        @test_router.post("/test/content-type")
        async def raise_duplicate():
            entity_type = "Product"
            field = "sku"
            value = "ABC-123"
            raise DuplicateEntityException(entity_type, field, value)

        app.include_router(test_router)

        with TestClient(app) as client:
            response = client.post("/test/content-type")

            assert response.headers["content-type"].startswith("application/problem+json")
            assert response.status_code == 409
