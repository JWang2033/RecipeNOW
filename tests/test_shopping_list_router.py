# tests/test_shopping_list_router.py
import json
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient


def _fake_vertex_response_json() -> Dict[str, Any]:
    """
    模拟 Vertex generateContent 的返回结构：
    data["candidates"][0]["content"]["parts"][0]["text"]
    里是一段 JSON 字符串（数组）。
    """
    shopping_list_json_str = json.dumps(
        [
            {
                "name": "egg",
                "quantity": 1,
                "unit": "pcs",
                "reason": "Recipe needs 3 eggs, pantry has 2, so buy 1 more.",
                "matched_existing": ["egg"],
                "matched_recipe": ["large egg"],
            }
        ]
    )

    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": shopping_list_json_str
                        }
                    ]
                }
            }
        ]
    }


def test_generate_shopping_list_missing_fields(client: TestClient):
    """
    当缺少 pantry_ingredients 或 recipe_ingredients 时，应返回 400。
    这个错误在你的 router 逻辑里就会被触发（而不是 Pydantic 验证）。
    """
    payload = {
        "pantry_ingredients": [{"name": "egg", "quantity": 2, "unit": "pcs"}]
        # 缺少 "recipe_ingredients"
    }

    resp = client.post("/shopping-list/generate", json=payload)
    assert resp.status_code == 400
    data = resp.json()
    assert "detail" in data


def test_generate_shopping_list_success(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    """
    正常请求时：
    - mock 掉 Vertex 的 access token 获取 + HTTP 请求
    - 检查返回结构和假数据一致
    """
    from backend.routers import shopping_list_router

    # 1. mock 掉 _get_vertex_access_token（如果你后面删掉了这个函数，这里可以改用 mock service_account）
    if hasattr(shopping_list_router, "_get_vertex_access_token"):
        monkeypatch.setattr(
            shopping_list_router, "_get_vertex_access_token", lambda: "fake-token"
        )

    # 2. mock 掉 requests.post
    class DummyResponse:
        def __init__(self, status_code: int = 200):
            self.status_code = status_code

        def json(self):
            return _fake_vertex_response_json()

    def fake_post(url, headers=None, json=None, timeout=None):
        return DummyResponse(status_code=200)

    monkeypatch.setattr(shopping_list_router.requests, "post", fake_post)

    # 3. 发送一个正常的请求
    payload = {
        "pantry_ingredients": [
            {"name": "egg", "quantity": 2, "unit": "pcs"},
            {"name": "milk", "quantity": 200, "unit": "ml"},
        ],
        "recipe_ingredients": [
            {"name": "large egg", "quantity": 3, "unit": "pcs"},
            {"name": "whole milk", "quantity": 300, "unit": "ml"},
        ],
    }

    resp = client.post("/shopping-list/generate", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert "to_buy" in data
    assert isinstance(data["to_buy"], list)
    assert len(data["to_buy"]) == 1

    item = data["to_buy"][0]
    assert item["name"] == "egg"
    assert item["quantity"] == 1
    assert item["unit"] == "pcs"
    assert item["matched_existing"] == ["egg"]
    assert item["matched_recipe"] == ["large egg"]

    # 调试字段也顺便看一下
    assert "shopping_list_raw" in data
    assert "raw_vertex" in data
