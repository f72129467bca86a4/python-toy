"""Integration tests for Petstore API endpoints."""

from __future__ import annotations

import re
import uuid
from typing import Any

from fastapi.testclient import TestClient

# UUID pattern for validation
UUID_PATTERN = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"


def assert_uuid_format(value: str) -> None:
    """Assert that a value matches UUID format."""
    assert re.match(UUID_PATTERN, value), f"Expected UUID format, got: {value}"


def assert_empty_response(response_data: dict[str, Any]) -> None:
    """Assert that response is empty (per design convention)."""
    assert response_data == {}


class TestPetAPI:
    """Test Pet API endpoints."""

    def test_pet_crud_lifecycle(self, client: TestClient) -> None:
        """Test complete Pet CRUD lifecycle."""
        # Create
        pet_data = {"name": "fluffy", "tags": ["cat", "cute"]}
        response = client.post("/v1/pets", json=pet_data)
        assert response.status_code == 201

        pet = response.json()
        assert_uuid_format(pet["id"])
        assert pet["name"] == "fluffy"
        assert sorted(pet["tags"]) == ["cat", "cute"]
        pet_id = pet["id"]

        # Read
        response = client.get(f"/v1/pets/{pet_id}")
        assert response.status_code == 200
        retrieved_pet = response.json()
        assert retrieved_pet["id"] == pet_id
        assert retrieved_pet["name"] == "fluffy"

        # Update
        update_data = {"name": "fluffy_updated"}
        response = client.patch(f"/v1/pets/{pet_id}", json=update_data)
        assert response.status_code == 200
        updated_pet = response.json()
        assert updated_pet["name"] == "fluffy_updated"
        assert updated_pet["id"] == pet_id

        # Delete
        response = client.delete(f"/v1/pets/{pet_id}")
        assert response.status_code == 200
        assert_empty_response(response.json())

        # Verify deletion
        response = client.get(f"/v1/pets/{pet_id}")
        assert response.status_code == 404

    def test_pet_list(self, client: TestClient) -> None:
        """Test Pet listing with pagination."""
        # Create test pets
        pet_ids = []
        for i in range(3):
            response = client.post("/v1/pets", json={"name": f"pet_{i}", "tags": []})
            assert response.status_code == 201
            pet_ids.append(response.json()["id"])

        try:
            # Test listing
            response = client.get("/v1/pets", params={"page": 1, "size": 10})
            assert response.status_code == 200

            page_data = response.json()
            assert isinstance(page_data["items"], list)
            assert len(page_data["items"]) >= 3
            assert page_data["page"] == 1
            assert page_data["size"] == 10

        finally:
            # Cleanup
            for pet_id in pet_ids:
                client.delete(f"/v1/pets/{pet_id}")

    def test_pet_with_relationships(self, client: TestClient) -> None:
        """Test Pet creation with category and owner relationships."""
        # Setup: Create category and user
        category_data = {"name": f"test_category_{uuid.uuid4().hex[:8]}"}
        response = client.post("/v1/categories", json=category_data)
        assert response.status_code == 201
        category_id = response.json()["id"]

        user_data = {
            "username": f"testuser_{uuid.uuid4().hex[:8]}",
            "first_name": "Test",
            "last_name": "User",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "password123",
        }
        response = client.post("/v1/users", json=user_data)
        assert response.status_code == 201
        user_id = response.json()["id"]

        try:
            # Create pet with relationships
            pet_data = {
                "name": "relationship_pet",
                "category_id": category_id,
                "owner_id": user_id,
                "tags": ["test"],
                "status": "available",
            }
            response = client.post("/v1/pets", json=pet_data)
            assert response.status_code == 201

            pet = response.json()
            pet_id = pet["id"]
            assert pet["category"]["id"] == category_id
            assert pet["owner"]["id"] == user_id
            assert pet["tags"] == ["test"]

            # Verify relationships in GET
            response = client.get(f"/v1/pets/{pet_id}")
            assert response.status_code == 200
            retrieved_pet = response.json()
            assert retrieved_pet["category"]["id"] == category_id
            assert retrieved_pet["owner"]["id"] == user_id

            # Cleanup pet
            client.delete(f"/v1/pets/{pet_id}")

        finally:
            # Cleanup relationships
            client.delete(f"/v1/users/{user_id}")
            client.delete(f"/v1/categories/{category_id}")


class TestCategoryAPI:
    """Test Category API endpoints."""

    def test_category_crud_lifecycle(self, client: TestClient) -> None:
        """Test complete Category CRUD lifecycle."""
        category_name = f"test_category_{uuid.uuid4().hex[:8]}"

        # Create
        response = client.post("/v1/categories", json={"name": category_name})
        assert response.status_code == 201

        category = response.json()
        assert_uuid_format(category["id"])
        assert category["name"] == category_name
        category_id = category["id"]

        # Read
        response = client.get(f"/v1/categories/{category_id}")
        assert response.status_code == 200
        retrieved_category = response.json()
        assert retrieved_category["id"] == category_id
        assert retrieved_category["name"] == category_name

        # List
        response = client.get("/v1/categories")
        assert response.status_code == 200
        page_data = response.json()
        assert isinstance(page_data["items"], list)

        # Delete
        response = client.delete(f"/v1/categories/{category_id}")
        assert response.status_code == 200
        assert_empty_response(response.json())

        # Verify deletion
        response = client.get(f"/v1/categories/{category_id}")
        assert response.status_code == 404


class TestTagAPI:
    """Test Tag API endpoints."""

    def test_tag_crud_lifecycle(self, client: TestClient) -> None:
        """Test complete Tag CRUD lifecycle."""
        tag_name = f"test_tag_{uuid.uuid4().hex[:8]}"

        # Create
        response = client.post("/v1/tags", json={"name": tag_name})
        assert response.status_code == 201

        tag = response.json()
        assert_uuid_format(tag["id"])
        assert tag["name"] == tag_name
        tag_id = tag["id"]

        # Read
        response = client.get(f"/v1/tags/{tag_id}")
        assert response.status_code == 200
        retrieved_tag = response.json()
        assert retrieved_tag["name"] == tag_name

        # List
        response = client.get("/v1/tags")
        assert response.status_code == 200
        page_data = response.json()
        assert isinstance(page_data["items"], list)

        # Delete
        response = client.delete(f"/v1/tags/{tag_id}")
        assert response.status_code == 200
        assert_empty_response(response.json())

        # Verify deletion
        response = client.get(f"/v1/tags/{tag_id}")
        assert response.status_code == 404


class TestUserAPI:
    """Test User API endpoints."""

    def test_user_crud_lifecycle(self, client: TestClient) -> None:
        """Test complete User CRUD lifecycle."""
        username = f"testuser_{uuid.uuid4().hex[:8]}"
        user_data = {
            "username": username,
            "first_name": "Test",
            "last_name": "User",
            "email": f"{username}@example.com",
            "password": "password123",
            "phone": "+1-555-0123",
        }

        # Create
        response = client.post("/v1/users", json=user_data)
        assert response.status_code == 201

        user = response.json()
        assert_uuid_format(user["id"])
        assert user["username"] == username
        assert user["email"] == user_data["email"]
        user_id = user["id"]

        # Read
        response = client.get(f"/v1/users/{user_id}")
        assert response.status_code == 200
        retrieved_user = response.json()
        assert retrieved_user["username"] == username

        # List
        response = client.get("/v1/users")
        assert response.status_code == 200
        page_data = response.json()
        assert isinstance(page_data["items"], list)

        # Delete
        response = client.delete(f"/v1/users/{user_id}")
        assert response.status_code == 200
        assert_empty_response(response.json())

        # Verify deletion
        response = client.get(f"/v1/users/{user_id}")
        assert response.status_code == 404


class TestValidationErrors:
    """Test API validation error handling."""

    def test_pet_validation_errors(self, client: TestClient) -> None:
        """Test Pet validation error responses."""
        # Empty name should fail
        response = client.post("/v1/pets", json={"name": "", "tags": []})
        assert response.status_code == 400
        assert response.headers["content-type"].startswith("application/problem+json")

        error_data = response.json()
        assert error_data["status"] == 400
        assert "errors" in error_data

    def test_nonexistent_resource_404(self, client: TestClient) -> None:
        """Test 404 responses for nonexistent resources."""
        fake_id = str(uuid.uuid4())

        for endpoint in [
            f"/v1/pets/{fake_id}",
            f"/v1/categories/{fake_id}",
            f"/v1/tags/{fake_id}",
            f"/v1/users/{fake_id}",
        ]:
            response = client.get(endpoint)
            assert response.status_code == 404
