"""Tests for root application metadata."""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestRootMetadata:
    """Test root application endpoints and metadata."""

    def test_root_service_metadata(self, client: TestClient) -> None:
        """Test that root endpoint returns correct service metadata."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "python-toy"
