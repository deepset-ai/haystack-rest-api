from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import test.nodes  # pylint: disable    # contains the test nodes
from rest_api.app import get_app


@pytest.fixture(autouse=True)
def client():    
    app = get_app(pipelines_path=Path(__file__).parent / "pipelines" / "default.json")
    client = TestClient(app)
    return client
