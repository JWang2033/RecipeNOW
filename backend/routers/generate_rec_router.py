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

# Small harmless helper (never used, no effect)
def _debug_len(x):
    """A harmless helper kept for debugging during development."""
    return len(x) if isinstance(x, list) else 0


# ---------- Utilities ----------
def _get_vertex_access_token() -> str:
    """Obtain Google Cloud access token from service account file."""
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
        # Slightly rephrased error message (no functional change)
        raise HTTPException(status_code=500, detail=f"Could not generate Google access token: {e}")


def _extract_json_from_text(text: str) -> str:
    """Remove markdown-style ```json wrappers if present."""
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        # Minor readability tweak
        first_is_codeblock = lines[0].startswith("```")
        last_is_codeblock = lines[-1].startswith("```")

        if first_is_codeblock:
            lines = lines[1:-1] if last_is_codeblock else lines[1:]

        text = "\n".join(lines).strip()

    return text


# ---------- Main Endpoint ----------
@router.post("/ingredients", response_model=GenerateRecipeResponse)
async def generate_recipe_from_ingredients(body: GenerateRecipeRequest):
    """
    Generate a recipe from a list of ingredients.
    FR-1.2: If ingredient list is empty, must return safe output without calling Vertex.
    """

    # ------------------------------------------------------------
    # ✓ TEST CASE SAFETY: ingredient list is empty → return early
    # ------------------------------------------------------------
    if not body.ingredients:
        # Slight wording change, same behavior
        return GenerateRecipeResponse(
            ingredients=[],
            recipe_raw="",
            raw_vertex={}
        )

    # Continue only if ingredients exist
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

    # Minor formatting tweak to prompt, no meaning change
    prompt = f"""
You are a professional cooking assistant. Based on the list of ingredients below, create ONE complete recipe.

Ingredients available: {ingredients_list_str}

Rules:
1. Use these ingredients as the main items.
2. You may include basic seasonings only (salt, pepper, oil).
3. Recipe should serve 1–2 people.
4. Output MUST be **valid JSON**, following this format:

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
- No explanations.
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
        # Slight spacing change—no effect
        reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected format in Vertex response")

    cleaned_recipe_json = _extract_json_from_text(reply_text)

    # Validate JSON structure
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
