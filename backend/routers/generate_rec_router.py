# backend/routers/generate_recipe_router.py

import os
import json
from typing import List

import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from google.oauth2 import service_account
from google.auth.transport.requests import Request as GoogleAuthRequest


router = APIRouter(prefix="/generate", tags=["Generate Recipe"])


# ---------- Request / Response Models ----------
class GenerateRecipeRequest(BaseModel):
    ingredients: List[str]


class GenerateRecipeResponse(BaseModel):
    ingredients: List[str]
    recipe_raw: str | None = ""
    raw_vertex: dict | None = {}


# ---------- Utilities ----------
def _get_vertex_access_token() -> str:
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise HTTPException(status_code=500, detail="GOOGLE_APPLICATION_CREDENTIALS is not configured")

    try:
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        creds = service_account.Credentials.from_service_account_file(
            cred_path, scopes=scopes
        )
        creds.refresh(GoogleAuthRequest())
        return creds.token
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to obtain Google access token: {e}")


def _extract_json_from_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 2 and lines[0].startswith("```"):
            if lines[-1].startswith("```"):
                lines = lines[1:-1]
            else:
                lines = lines[1:]
        text = "\n".join(lines).strip()
    return text


# ---------- Main Endpoint ----------
@router.post("/ingredients", response_model=GenerateRecipeResponse)
async def generate_recipe_from_ingredients(body: GenerateRecipeRequest):
    """
    Generate a recipe from a list of ingredients.
    Must gracefully handle empty ingredient list per FR-1.2.
    """

    # ============================================================
    # 🔥 SPECIAL REQUIREMENT FOR TEST CASE 2
    # If the ingredient list is empty (due to low-quality scan),
    # DO NOT CALL Vertex, return expected test-case-safe output.
    # ============================================================
    if not body.ingredients:
        return GenerateRecipeResponse(
            ingredients=[],
            recipe_raw="",
            raw_vertex={}
        )

    # ============================================================
    # Continue only if ingredients are valid
    # ============================================================
    project_id = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GCP_LOCATION", "us-central1")

    if not project_id:
        raise HTTPException(status_code=500, detail="GCP_PROJECT_ID is not configured")

    access_token = _get_vertex_access_token()

    model = "gemini-2.5-flash"
    url = (
        f"https://{location}-aiplatform.googleapis.com/v1/"
        f"projects/{project_id}/locations/{location}/publishers/google/"
        f"models/{model}:generateContent"
    )

    ingredients_list_str = ", ".join(body.ingredients)

    # English-only recipe generation prompt
    prompt = f"""
You are a professional cooking assistant. Based on the list of available ingredients below,
create ONE complete recipe.

Available ingredients: {ingredients_list_str}

Requirements:
1. Use the provided ingredients as primary components.
2. You may add basic seasonings (salt, pepper, oil) but avoid unrelated ingredients.
3. Recipe must serve 1–2 people.
4. Output strictly **valid JSON** in the exact structure below:

{{
  "title": "Example Dish Name",
  "servings": 2,
  "ingredients": [
    {{
      "name": "ingredient name",
      "amount": 100,
      "unit": "g"
    }}
  ],
  "steps": [
    "Step 1 ...",
    "Step 2 ..."
  ],
  "estimated_time_minutes": 20,
  "difficulty": "easy"
}}

Important:
- Return JSON only.
- Do NOT include explanations or comments.
""".strip()

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.6},
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=resp.text)

    data = resp.json()

    try:
        reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected Vertex response format")

    cleaned_recipe_json = _extract_json_from_text(reply_text)

    # Validate JSON
    try:
        json.loads(cleaned_recipe_json)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"Vertex returned invalid JSON: {cleaned_recipe_json[:200]}..."
        )

    return GenerateRecipeResponse(
        ingredients=body.ingredients,
        recipe_raw=cleaned_recipe_json,
        raw_vertex=data,
    )