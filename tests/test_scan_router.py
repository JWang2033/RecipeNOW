# tests/test_scan_router.py
import json
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient


def _fake_vertex_scan_response() -> Dict[str, Any]:
    """
    模拟 Vertex Vision 模型的返回结构，Text 里放一个 JSON 字符串数组。
    """
    ingredients_json_str = json.dumps(
        [
            {"name": "mango slices", "category": "fruit", "confidence": 0.98},
            {"name": "tapioca pearls", "category": "starch", "confidence": 0.95},
        ]
    )

    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": ingredients_json_str
                        }
                    ]
                }
            }
        ]
    }


def test_scan_ingredients_validation_error(client: TestClient):
    """
    不传 file 的情况下，请求 /scan/ingredients 应该返回 422（请求体验证错误），
    这是 FastAPI 层的验证。
    """
    resp = client.post("/scan/ingredients")
    assert resp.status_code == 422  # 缺少必需的 file 字段


def test_scan_ingredients_success(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    """
    正常上传图片时：
    - mock 掉 service account 获取 token + requests.post
    - 检查返回 200，且 JSON 结构大致正确
    """
    from backend.routers import scan_router

    # 1. mock 掉 Google service account（避免去读本地 JSON 文件）
    class DummyCreds:
        def __init__(self, *args, **kwargs):
            self.token = "fake-token"

        def refresh(self, req):
            self.token = "fake-token"

    if hasattr(scan_router, "service_account"):
        monkeypatch.setattr(
            scan_router.service_account.Credentials,
            "from_service_account_file",
            lambda *args, **kwargs: DummyCreds(),
        )

    # 如果你在 scan_router 里有单独的 _get_vertex_access_token，也可以直接 mock 那个：
    if hasattr(scan_router, "_get_vertex_access_token"):
        monkeypatch.setattr(
            scan_router, "_get_vertex_access_token", lambda: "fake-token"
        )

    # 2. mock 掉 requests.post
    class DummyResponse:
        def __init__(self, status_code: int = 200):
            self.status_code = status_code

        def json(self):
            return _fake_vertex_scan_response()

    monkeypatch.setattr(scan_router.requests, "post", lambda *a, **k: DummyResponse())

    # 3. 发送一个带文件的请求
    files = {
        "file": ("test.jpg", b"fake-image-bytes", "image/jpeg")
    }

    resp = client.post("/scan/ingredients", files=files)
    assert resp.status_code == 200

    data = resp.json()
    # 下面根据你 scan_router 的实现做一些宽松检查：
    # 如果你有 "ingredients" 字段：
    if "ingredients" in data:
        assert isinstance(data["ingredients"], list)
        assert len(data["ingredients"]) == 2
    # 如果你只返回了 "ingredients_raw"：
    if "ingredients_raw" in data:
        assert isinstance(data["ingredients_raw"], str)
