# tests/test_generate_recipe_router.py
import json

import pytest
from fastapi.testclient import TestClient


def _fake_vertex_recipe_response():
    """
    模拟 Vertex generateContent 的返回结构：
    data["candidates"][0]["content"]["parts"][0]["text"]
    里是一段 JSON 字符串（单个 recipe 对象）。
    """
    recipe_json_str = json.dumps(
        {
            "title": "Simple Egg Toast",
            "servings": 1,
            "ingredients": [
                {"name": "egg", "amount": 1, "unit": "pcs"},
                {"name": "bread", "amount": 1, "unit": "slice"},
            ],
            "steps": [
                "Beat the egg.",
                "Toast the bread and top with egg.",
            ],
            "estimated_time_minutes": 10,
            "difficulty": "easy",
        }
    )

    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": recipe_json_str
                        }
                    ]
                }
            }
        ]
    }


def test_generate_recipe_empty_ingredients_returns_empty(client: TestClient):
    """
    当 ingredients 为空时，应走 FR-1.2 的特殊分支：
    - 不调用 Vertex
    - 返回空的 recipe_raw 和 raw_vertex
    """
    payload = {"ingredients": []}

    resp = client.post("/generate/ingredients", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert data["ingredients"] == []
    assert data["recipe_raw"] == ""
    assert data["raw_vertex"] == {}


def test_generate_recipe_success(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    """
    正常有 ingredients 时：
    - mock 掉 _get_vertex_access_token（不读本地 key）
    - mock 掉 requests.post（不访问外网）
    - 检查返回结构和 fake 响应一致，且 recipe_raw 是合法 JSON
    """
    from backend.routers import generate_rec_router

    # 1. mock 掉 _get_vertex_access_token，避免依赖 GCP 凭证文件
    monkeypatch.setattr(
        generate_rec_router, "_get_vertex_access_token", lambda: "fake-token"
    )

    # 2. mock 掉 requests.post，返回我们构造的假 Vertex 响应
    class DummyResponse:
        def __init__(self, status_code: int = 200):
            self.status_code = status_code

        def json(self):
            return _fake_vertex_recipe_response()

    monkeypatch.setattr(
        generate_rec_router.requests, "post",
        lambda *a, **k: DummyResponse()
    )

    # 3. 发送一个正常的请求
    payload = {"ingredients": ["egg", "milk", "sugar"]}

    resp = client.post("/generate/ingredients", json=payload)
    assert resp.status_code == 200

    data = resp.json()

    # ingredients 应该原样返回
    assert data["ingredients"] == payload["ingredients"]

    # recipe_raw 应该是非空字符串，并且能被 json.loads 解析
    assert isinstance(data["recipe_raw"], str)
    assert data["recipe_raw"].strip() != ""

    recipe_obj = json.loads(data["recipe_raw"])
    assert recipe_obj["title"] == "Simple Egg Toast"
    assert recipe_obj["servings"] == 1
    assert isinstance(recipe_obj["ingredients"], list)
    assert isinstance(recipe_obj["steps"], list)

    # raw_vertex 应该也存在（方便调试）
    assert "raw_vertex" in data
    assert isinstance(data["raw_vertex"], dict)
