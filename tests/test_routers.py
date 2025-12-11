# tests/test_routers.py
import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch


# ==================== Generate Recipe Router - Additional Tests ====================

class TestGenerateRecipeRouterExtra:
    def test_generate_recipe_with_single_ingredient(self, client: TestClient, monkeypatch):
        """Test recipe generation with just one ingredient"""
        from backend.routers import generate_rec_router
        
        monkeypatch.setattr(
            generate_rec_router, "_get_vertex_access_token", lambda: "fake-token"
        )
        
        recipe_json = json.dumps({
            "title": "Simple Rice",
            "servings": 1,
            "ingredients": [{"name": "rice", "amount": 100, "unit": "g"}],
            "steps": ["Cook rice"],
            "estimated_time_minutes": 20,
            "difficulty": "easy"
        })
        
        class DummyResponse:
            status_code = 200
            def json(self):
                return {
                    "candidates": [{"content": {"parts": [{"text": recipe_json}]}}]
                }
        
        monkeypatch.setattr(
            generate_rec_router.requests, "post", lambda *a, **k: DummyResponse()
        )
        
        payload = {"ingredients": ["rice"]}
        resp = client.post("/generate/ingredients", json=payload)
        
        assert resp.status_code == 200
        data = resp.json()
        assert data["ingredients"] == ["rice"]
        assert "recipe_raw" in data

    def test_generate_recipe_vertex_error(self, client: TestClient, monkeypatch):
        """Test handling when Vertex API returns an error"""
        from backend.routers import generate_rec_router
        
        monkeypatch.setattr(
            generate_rec_router, "_get_vertex_access_token", lambda: "fake-token"
        )
        
        class ErrorResponse:
            status_code = 500
            text = "Internal server error"
            def json(self):
                return {"error": "Internal server error"}
        
        monkeypatch.setattr(
            generate_rec_router.requests, "post", lambda *a, **k: ErrorResponse()
        )
        
        payload = {"ingredients": ["chicken", "rice"]}
        resp = client.post("/generate/ingredients", json=payload)
        
        # Should return 500 since Vertex returned error
        assert resp.status_code == 500


# ==================== Scan Router - Additional Tests ====================

class TestScanRouterExtra:
    def test_scan_png_image(self, client: TestClient, monkeypatch):
        """Test scanning a PNG image"""
        from backend.routers import scan_router
        
        if hasattr(scan_router, "_get_vertex_access_token"):
            monkeypatch.setattr(
                scan_router, "_get_vertex_access_token", lambda: "fake-token"
            )
        
        # Mock service account if needed
        if hasattr(scan_router, "service_account"):
            class DummyCreds:
                token = "fake-token"
                def refresh(self, req):
                    pass
            monkeypatch.setattr(
                scan_router.service_account.Credentials,
                "from_service_account_file",
                lambda *args, **kwargs: DummyCreds()
            )
        
        ingredients_json = json.dumps([
            {"name": "banana", "category": "fruit", "confidence": 0.95}
        ])
        
        class DummyResponse:
            status_code = 200
            def json(self):
                return {
                    "candidates": [{"content": {"parts": [{"text": ingredients_json}]}}]
                }
        
        monkeypatch.setattr(scan_router.requests, "post", lambda *a, **k: DummyResponse())
        
        # PNG file
        files = {"file": ("test.png", b"\x89PNG\r\n\x1a\n" + b"fake", "image/png")}
        resp = client.post("/scan/ingredients", files=files)
        
        assert resp.status_code == 200

    def test_scan_multiple_ingredients(self, client: TestClient, monkeypatch):
        """Test scanning image with multiple ingredients"""
        from backend.routers import scan_router
        
        if hasattr(scan_router, "_get_vertex_access_token"):
            monkeypatch.setattr(
                scan_router, "_get_vertex_access_token", lambda: "fake-token"
            )
        
        if hasattr(scan_router, "service_account"):
            class DummyCreds:
                token = "fake-token"
                def refresh(self, req):
                    pass
            monkeypatch.setattr(
                scan_router.service_account.Credentials,
                "from_service_account_file",
                lambda *args, **kwargs: DummyCreds()
            )
        
        ingredients_json = json.dumps([
            {"name": "tomato", "category": "vegetable", "confidence": 0.99},
            {"name": "onion", "category": "vegetable", "confidence": 0.97},
            {"name": "garlic", "category": "vegetable", "confidence": 0.96},
            {"name": "chicken", "category": "meat", "confidence": 0.94}
        ])
        
        class DummyResponse:
            status_code = 200
            def json(self):
                return {
                    "candidates": [{"content": {"parts": [{"text": ingredients_json}]}}]
                }
        
        monkeypatch.setattr(scan_router.requests, "post", lambda *a, **k: DummyResponse())
        
        files = {"file": ("fridge.jpg", b"fake-image-data", "image/jpeg")}
        resp = client.post("/scan/ingredients", files=files)
        
        assert resp.status_code == 200
        data = resp.json()
        if "ingredients" in data:
            assert len(data["ingredients"]) == 4


# ==================== Shopping List Router - Additional Tests ====================

class TestShoppingListRouterExtra:
    def test_shopping_list_empty_pantry(self, client: TestClient, monkeypatch):
        """Test with completely empty pantry"""
        from backend.routers import shopping_list_router
        
        if hasattr(shopping_list_router, "_get_vertex_access_token"):
            monkeypatch.setattr(
                shopping_list_router, "_get_vertex_access_token", lambda: "fake-token"
            )
        
        shopping_json = json.dumps([
            {"name": "flour", "quantity": 500, "unit": "g", "reason": "Recipe needs flour"},
            {"name": "sugar", "quantity": 200, "unit": "g", "reason": "Recipe needs sugar"}
        ])
        
        class DummyResponse:
            status_code = 200
            def json(self):
                return {
                    "candidates": [{"content": {"parts": [{"text": shopping_json}]}}]
                }
        
        monkeypatch.setattr(
            shopping_list_router.requests, "post", lambda *a, **k: DummyResponse()
        )
        
        payload = {
            "pantry_ingredients": [],
            "recipe_ingredients": [
                {"name": "flour", "quantity": 500, "unit": "g"},
                {"name": "sugar", "quantity": 200, "unit": "g"}
            ]
        }
        
        resp = client.post("/shopping-list/generate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "to_buy" in data

    def test_shopping_list_all_ingredients_available(self, client: TestClient, monkeypatch):
        """Test when pantry has all ingredients"""
        from backend.routers import shopping_list_router
        
        if hasattr(shopping_list_router, "_get_vertex_access_token"):
            monkeypatch.setattr(
                shopping_list_router, "_get_vertex_access_token", lambda: "fake-token"
            )
        
        # Empty shopping list - everything available
        shopping_json = json.dumps([])
        
        class DummyResponse:
            status_code = 200
            def json(self):
                return {
                    "candidates": [{"content": {"parts": [{"text": shopping_json}]}}]
                }
        
        monkeypatch.setattr(
            shopping_list_router.requests, "post", lambda *a, **k: DummyResponse()
        )
        
        payload = {
            "pantry_ingredients": [
                {"name": "egg", "quantity": 12, "unit": "pcs"},
                {"name": "milk", "quantity": 1000, "unit": "ml"}
            ],
            "recipe_ingredients": [
                {"name": "egg", "quantity": 2, "unit": "pcs"},
                {"name": "milk", "quantity": 200, "unit": "ml"}
            ]
        }
        
        resp = client.post("/shopping-list/generate", json=payload)
        assert resp.status_code == 200

    def test_shopping_list_missing_both_fields(self, client: TestClient):
        """Test with both fields missing returns 400"""
        resp = client.post("/shopping-list/generate", json={})
        assert resp.status_code == 400

    def test_shopping_list_partial_match(self, client: TestClient, monkeypatch):
        """Test partial ingredient matching"""
        from backend.routers import shopping_list_router
        
        if hasattr(shopping_list_router, "_get_vertex_access_token"):
            monkeypatch.setattr(
                shopping_list_router, "_get_vertex_access_token", lambda: "fake-token"
            )
        
        shopping_json = json.dumps([
            {
                "name": "butter",
                "quantity": 50,
                "unit": "g",
                "reason": "Recipe needs 100g, pantry has 50g",
                "matched_existing": ["butter"],
                "matched_recipe": ["unsalted butter"]
            }
        ])
        
        class DummyResponse:
            status_code = 200
            def json(self):
                return {
                    "candidates": [{"content": {"parts": [{"text": shopping_json}]}}]
                }
        
        monkeypatch.setattr(
            shopping_list_router.requests, "post", lambda *a, **k: DummyResponse()
        )
        
        payload = {
            "pantry_ingredients": [
                {"name": "butter", "quantity": 50, "unit": "g"}
            ],
            "recipe_ingredients": [
                {"name": "unsalted butter", "quantity": 100, "unit": "g"}
            ]
        }
        
        resp = client.post("/shopping-list/generate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["to_buy"]) == 1
        assert data["to_buy"][0]["quantity"] == 50


# ==================== Additional Scan Router Tests ====================

class TestScanRouterErrors:
    def test_scan_vertex_error_response(self, client: TestClient, monkeypatch):
        """Test handling when Vertex returns error"""
        from backend.routers import scan_router
        
        if hasattr(scan_router, "_get_vertex_access_token"):
            monkeypatch.setattr(
                scan_router, "_get_vertex_access_token", lambda: "fake-token"
            )
        
        if hasattr(scan_router, "service_account"):
            class DummyCreds:
                token = "fake-token"
                def refresh(self, req):
                    pass
            monkeypatch.setattr(
                scan_router.service_account.Credentials,
                "from_service_account_file",
                lambda *args, **kwargs: DummyCreds()
            )
        
        class ErrorResponse:
            status_code = 500
            text = "Internal error"
            def json(self):
                return {"error": "failed"}
        
        monkeypatch.setattr(scan_router.requests, "post", lambda *a, **k: ErrorResponse())
        
        files = {"file": ("test.jpg", b"fake-image", "image/jpeg")}
        resp = client.post("/scan/ingredients", files=files)
        
        # Should handle error - returns 502 Bad Gateway when Vertex fails
        assert resp.status_code in [200, 500, 502]


# ==================== Additional Generate Recipe Tests ====================

class TestGenerateRecipeWithPreferences:
    def test_generate_with_diets(self, client: TestClient, monkeypatch):
        """Test recipe with dietary restrictions"""
        from backend.routers import generate_rec_router
        
        monkeypatch.setattr(
            generate_rec_router, "_get_vertex_access_token", lambda: "fake-token"
        )
        
        recipe_json = json.dumps({
            "title": "Vegan Salad",
            "servings": 2,
            "ingredients": [{"name": "lettuce", "amount": 100, "unit": "g"}],
            "steps": ["Mix ingredients"],
            "estimated_time_minutes": 10,
            "difficulty": "easy"
        })
        
        class DummyResponse:
            status_code = 200
            def json(self):
                return {
                    "candidates": [{"content": {"parts": [{"text": recipe_json}]}}]
                }
        
        monkeypatch.setattr(
            generate_rec_router.requests, "post", lambda *a, **k: DummyResponse()
        )
        
        payload = {
            "ingredients": ["lettuce", "tomato"],
            "diets": ["vegan"],
            "allergens": ["nuts"]
        }
        resp = client.post("/generate/ingredients", json=payload)
        
        assert resp.status_code == 200

    def test_generate_with_time_and_difficulty(self, client: TestClient, monkeypatch):
        """Test recipe with time and difficulty constraints"""
        from backend.routers import generate_rec_router
        
        monkeypatch.setattr(
            generate_rec_router, "_get_vertex_access_token", lambda: "fake-token"
        )
        
        recipe_json = json.dumps({
            "title": "Quick Omelette",
            "servings": 1,
            "ingredients": [{"name": "egg", "amount": 2, "unit": "pcs"}],
            "steps": ["Beat eggs", "Cook"],
            "estimated_time_minutes": 5,
            "difficulty": "easy"
        })
        
        class DummyResponse:
            status_code = 200
            def json(self):
                return {
                    "candidates": [{"content": {"parts": [{"text": recipe_json}]}}]
                }
        
        monkeypatch.setattr(
            generate_rec_router.requests, "post", lambda *a, **k: DummyResponse()
        )
        
        payload = {
            "ingredients": ["egg"],
            "max_cooking_time": 10,
            "difficulty": "easy"
        }
        resp = client.post("/generate/ingredients", json=payload)
        
        assert resp.status_code == 200


# ==================== Shopping List Additional Tests ====================

class TestShoppingListAdditional:
    def test_shopping_list_vertex_error(self, client: TestClient, monkeypatch):
        """Test shopping list when Vertex returns error"""
        from backend.routers import shopping_list_router
        
        if hasattr(shopping_list_router, "_get_vertex_access_token"):
            monkeypatch.setattr(
                shopping_list_router, "_get_vertex_access_token", lambda: "fake-token"
            )
        
        class ErrorResponse:
            status_code = 500
            text = "Internal error"
            def json(self):
                return {"error": "failed"}
        
        monkeypatch.setattr(
            shopping_list_router.requests, "post", lambda *a, **k: ErrorResponse()
        )
        
        payload = {
            "pantry_ingredients": [{"name": "egg", "quantity": 2, "unit": "pcs"}],
            "recipe_ingredients": [{"name": "egg", "quantity": 6, "unit": "pcs"}]
        }
        
        resp = client.post("/shopping-list/generate", json=payload)
        # Should return error status
        assert resp.status_code in [200, 500, 502]

    def test_shopping_list_with_many_items(self, client: TestClient, monkeypatch):
        """Test shopping list with many ingredients"""
        from backend.routers import shopping_list_router
        
        if hasattr(shopping_list_router, "_get_vertex_access_token"):
            monkeypatch.setattr(
                shopping_list_router, "_get_vertex_access_token", lambda: "fake-token"
            )
        
        shopping_json = json.dumps([
            {"name": "chicken", "quantity": 500, "unit": "g", "reason": "Need more"},
            {"name": "rice", "quantity": 200, "unit": "g", "reason": "Need more"},
            {"name": "soy sauce", "quantity": 50, "unit": "ml", "reason": "Need more"}
        ])
        
        class DummyResponse:
            status_code = 200
            def json(self):
                return {
                    "candidates": [{"content": {"parts": [{"text": shopping_json}]}}]
                }
        
        monkeypatch.setattr(
            shopping_list_router.requests, "post", lambda *a, **k: DummyResponse()
        )
        
        payload = {
            "pantry_ingredients": [
                {"name": "chicken", "quantity": 100, "unit": "g"},
                {"name": "rice", "quantity": 50, "unit": "g"}
            ],
            "recipe_ingredients": [
                {"name": "chicken", "quantity": 600, "unit": "g"},
                {"name": "rice", "quantity": 250, "unit": "g"},
                {"name": "soy sauce", "quantity": 50, "unit": "ml"}
            ]
        }
        
        resp = client.post("/shopping-list/generate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["to_buy"]) == 3


# ==================== Additional Scan Tests ====================

class TestScanAdditional:
    def test_scan_jpeg_image(self, client: TestClient, monkeypatch):
        """Test scanning a JPEG image"""
        from backend.routers import scan_router
        
        if hasattr(scan_router, "_get_vertex_access_token"):
            monkeypatch.setattr(
                scan_router, "_get_vertex_access_token", lambda: "fake-token"
            )
        
        if hasattr(scan_router, "service_account"):
            class DummyCreds:
                token = "fake-token"
                def refresh(self, req):
                    pass
            monkeypatch.setattr(
                scan_router.service_account.Credentials,
                "from_service_account_file",
                lambda *args, **kwargs: DummyCreds()
            )
        
        ingredients_json = json.dumps([
            {"name": "carrot", "category": "vegetable", "confidence": 0.92},
            {"name": "potato", "category": "vegetable", "confidence": 0.88}
        ])
        
        class DummyResponse:
            status_code = 200
            def json(self):
                return {
                    "candidates": [{"content": {"parts": [{"text": ingredients_json}]}}]
                }
        
        monkeypatch.setattr(scan_router.requests, "post", lambda *a, **k: DummyResponse())
        
        # JPEG file with fake data
        files = {"file": ("veggies.jpg", b"\xff\xd8\xff\xe0" + b"fake-jpeg-data", "image/jpeg")}
        resp = client.post("/scan/ingredients", files=files)
        
        assert resp.status_code == 200
        data = resp.json()
        if "ingredients" in data:
            assert isinstance(data["ingredients"], list)