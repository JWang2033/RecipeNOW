# backend/routers/shopping_list_router.py
import os
import json
from typing import List, Any

import requests
from fastapi import APIRouter, HTTPException

from google.oauth2 import service_account
from google.auth.transport.requests import Request as GoogleAuthRequest


router = APIRouter(prefix="/shopping-list", tags=["Shopping List"])


# ---------- Shared utilities ----------
def _get_vertex_access_token() -> str:
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise HTTPException(status_code=500, detail="GOOGLE_APPLICATION_CREDENTIALS is not set")

    try:
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        creds = service_account.Credentials.from_service_account_file(
            cred_path, scopes=scopes
        )
        creds.refresh(GoogleAuthRequest())
        return creds.token
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Google access token: {e}")


def _extract_json_from_text(text: str) -> str:
    """
    Remove ```json ... ``` / ``` ... ``` wrappers and return the pure JSON string.
    """
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


# ---------- Main endpoint: generate shopping list ----------
@router.post("/generate")
async def generate_shopping_list(body: dict) -> dict:
    """
    Simplified version:
    - Input: raw JSON body with keys:
        {
          "pantry_ingredients": [...],
          "recipe_ingredients": [...]
        }
      Each ingredient can be any dict you like, we just serialize it for the model.
    - Output:
        {
          "to_buy": [...],              # parsed JSON array from Vertex
          "shopping_list_raw": "text",  # raw text from Vertex
          "raw_vertex": {...}           # full Vertex response (for debugging)
        }
    """
    project_id = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GCP_LOCATION", "us-central1")
    if not project_id:
        raise HTTPException(status_code=500, detail="GCP_PROJECT_ID is not set")

    # ---- 1. 取输入 & 基础校验 ----
    if "pantry_ingredients" not in body or "recipe_ingredients" not in body:
        raise HTTPException(
            status_code=400,
            detail="Request JSON must contain 'pantry_ingredients' and 'recipe_ingredients'.",
        )

    pantry_ingredients = body["pantry_ingredients"]
    recipe_ingredients = body["recipe_ingredients"]

    if not isinstance(pantry_ingredients, list) or not isinstance(recipe_ingredients, list):
        raise HTTPException(
            status_code=400,
            detail="'pantry_ingredients' and 'recipe_ingredients' must both be arrays.",
        )

    # ---- 2. 获取 access token ----
    access_token = _get_vertex_access_token()

    # ---- 3. 序列化成字符串（让模型去理解）----
    pantry_str = json.dumps(pantry_ingredients, ensure_ascii=False)
    recipe_str = json.dumps(recipe_ingredients, ensure_ascii=False)

    model = "gemini-2.5-flash"
    url = (
        f"https://{location}-aiplatform.googleapis.com/v1/"
        f"projects/{project_id}/locations/{location}/publishers/google/"
        f"models/{model}:generateContent"
    )

    prompt = """
IMPORTANT: Your entire response MUST be in ENGLISH ONLY.

- If the input ingredient names are in other languages, you MUST translate and normalize them to natural English cooking terms.
- The JSON you return must not contain any non-English text.

You are an intelligent shopping list assistant.

Your task: given a list of **pantry ingredients** (what the user already has) and a list of **recipe ingredients** (what the recipe requires), you must generate a list of ingredients that the user still needs to buy.

Input format:
- pantry_ingredients: JSON array of ingredients the user already has
- recipe_ingredients: JSON array of ingredients required by the recipe

Each ingredient object may look like:
{
  "name": "ingredient name (may be any language, but you must normalize to English in the OUTPUT)",
  "quantity": number or null,
  "unit": "unit string or null",
  "notes": "optional notes, e.g. 'large', 'diced', etc."
}

Your tasks:

1. Identify ingredients that are actually the same item even if named differently, for example:
   - "egg" vs "large egg" vs "eggs"
   - "onion" vs "red onion" (if the recipe explicitly requires a specific type, you may treat them as different when appropriate)
   - "coconut milk" vs "canned coconut milk"
   - Non-English names that refer to the same English ingredient should also be merged.
   Use semantic understanding, not just string matching.

2. For each ingredient required by the recipe:
   - If the user has **none** of that ingredient in the pantry, it must appear in the shopping list.
   - If the user has **insufficient quantity** (for example: recipe needs 500 g, pantry has 200 g), the shopping list should contain the **missing amount** (300 g).
   - If quantity or unit information is missing on either side, use a reasonable and conservative estimate based on common sense, or simply mark that some extra amount should be bought.

3. Merge duplicates:
   - If several recipe ingredients should be treated as the same purchase item (e.g. "egg 2 pcs" and "large egg 1 pc"), merge them into a single shopping list item with a unified name and total missing quantity.
   - For each unified item, you should track which original pantry and recipe ingredient names were matched into it.

Output format:
You must return **only** a JSON array. Each element represents one ingredient that needs to be purchased, with the structure:

[
  {
    "name": "unified purchase name in English",
    "quantity": number or null,
    "unit": "unit string or null",
    "reason": "short explanation in English why this needs to be bought and roughly how much",
    "matched_existing": ["matched pantry ingredient name 1 (original input text)", "pantry ingredient name 2", ...],
    "matched_recipe": ["matched recipe ingredient name 1 (original input text)", "recipe ingredient name 2", ...]
  },
  ...
]

Requirements:
- If the user does not need to buy anything, return an empty array: [].
- All names and text in the OUTPUT must be in English only.
- Return pure JSON only, with no extra explanations, comments, or additional fields.
    """.strip()

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {"text": "\n\npantry_ingredients (JSON):\n" + pantry_str},
                    {"text": "\n\nrecipe_ingredients (JSON):\n" + recipe_str},
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
        },
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    # ---- 4. 调用 Vertex ----
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=resp.text)

    data: dict = resp.json()

    try:
        reply_text: str = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected Vertex response")

    # ---- 5. 把模型的 JSON 字符串解析出来 ----
    cleaned = _extract_json_from_text(reply_text)
    try:
        to_buy: Any = json.loads(cleaned)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse Vertex shopping list JSON: {cleaned[:200]}..."
        )

    if not isinstance(to_buy, list):
        raise HTTPException(
            status_code=500,
            detail="Vertex shopping list top-level JSON must be an array"
        )

    # 不再做结构校验：直接把模型返回的数组塞回去
    return {
        "to_buy": to_buy,
        "shopping_list_raw": reply_text,
        "raw_vertex": data,
    }