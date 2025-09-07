from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from typing import Iterator

from python_toy.server.app import create_app
from python_toy.server.infra import health


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app()
    health.reset_state()

    with TestClient(app, raise_server_exceptions=False) as c:
        health.set_started()
        yield c
