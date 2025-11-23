# tests/conftest.py
import os

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture(scope="session", autouse=True)
def _set_test_env():
    """
    全局测试环境变量，避免 Vertex 相关 router 因为缺 GCP_PROJECT_ID 报错。
    """
    os.environ.setdefault("GCP_PROJECT_ID", "test-project")
    os.environ.setdefault("GCP_LOCATION", "us-central1")


@pytest.fixture
def client():
    """
    FastAPI TestClient，用来调用 HTTP 接口。
    """
    return TestClient(app)
