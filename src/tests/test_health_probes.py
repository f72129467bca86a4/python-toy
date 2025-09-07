from __future__ import annotations

from fastapi.testclient import TestClient

from python_toy.server.app import create_app
from python_toy.server.infra import health


def test_health_probes_transition():
    app = create_app()

    with TestClient(app) as client:
        health.reset_state()

        r = client.get("/.internal/healthz/liveness")
        assert r.status_code == 200, "Liveness should be always UP"
        assert r.text == "UP"

        r = client.get("/.internal/healthz/startup")
        assert r.status_code == 503, "Startup should be DOWN before started"
        assert r.text == "DOWN"

        r = client.get("/.internal/healthz/readiness")
        assert r.status_code == 503, "Readiness should be DOWN before started"
        assert r.text == "DOWN"

        health.set_started()

        r = client.get("/.internal/healthz/startup")
        assert r.status_code == 200, "Startup should be UP after started"
        assert r.text == "UP"

        r = client.get("/.internal/healthz/readiness")
        assert r.status_code == 200, "Readiness should be UP after started"
        assert r.text == "UP"
