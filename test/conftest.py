from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import test.nodes  # pylint: disable    # contains the test nodes
from rest_api.app import get_app
from rest_api.routers.pipelines import get_pipelines


@pytest.fixture(autouse=True)
def client():
    get_pipelines(pipelines_path=Path(__file__).parent / "pipelines" / "default.json")
    client = TestClient(get_app())
    return client
