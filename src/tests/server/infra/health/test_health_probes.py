"""Tests for health probe endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from python_toy.server.app import create_app
from python_toy.server.infra import health


class TestHealthProbes:
    """Test health probe endpoints and state transitions."""

    def test_health_probes_lifecycle(self) -> None:
        """Test complete health probe lifecycle from startup to ready."""
        app = create_app()

        with TestClient(app) as client:
            health.reset_state()

            # Test liveness - should always be UP
            response = client.get("/.internal/healthz/liveness")
            assert response.status_code == 200
            assert response.text == "UP"

            # Test startup probe - should be DOWN before started
            response = client.get("/.internal/healthz/startup")
            assert response.status_code == 503
            assert response.text == "DOWN"

            # Test readiness probe - should be DOWN before started
            response = client.get("/.internal/healthz/readiness")
            assert response.status_code == 503
            assert response.text == "DOWN"

            # Simulate application startup completion
            health.set_started()

            # Test startup probe - should be UP after started
            response = client.get("/.internal/healthz/startup")
            assert response.status_code == 200
            assert response.text == "UP"

            # Test readiness probe - should be UP after started
            response = client.get("/.internal/healthz/readiness")
            assert response.status_code == 200
            assert response.text == "UP"

            # Liveness should still be UP
            response = client.get("/.internal/healthz/liveness")
            assert response.status_code == 200
            assert response.text == "UP"
