# backend/routers/scan_ingredients_router.py (English version, enforced English output)

import os
import json
import base64
from typing import List

import requests
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from google.oauth2 import service_account
from google.auth.transport.requests import Request as GoogleAuthRequest

router = APIRouter(prefix="/scan", tags=["Scan Ingredients"])


# ---------- Response Model ----------
class ScanIngredientsResponse(BaseModel):
    ingredients: List[str]
    ingredients_raw: str
    raw_vertex: dict


# ---------- Internal Utility Functions ----------
def _get_vertex_access_token() -> str:
    """
    Obtain Google Cloud access token using a service account.
    Requires:
    - GOOGLE_APPLICATION_CREDENTIALS
    """
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
    Clean model output by removing ```json and ``` wrappers.
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


def _parse_ingredient_names(reply_text: str) -> List[str]:
    """
    Parse the Gemini model JSON response.
    Expects:
    [
      "mango slices",
      "coconut milk"
    ]
    """
    cleaned = _extract_json_from_text(reply_text)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse JSON from Vertex: {cleaned[:200]}..."
        )

    ingredients: List[str] = []

    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                ingredients.append(item.strip())
            elif isinstance(item, dict) and "name" in item:
                name = str(item["name"]).strip()
                if name:
                    ingredients.append(name)
            else:
                continue
    else:
        raise HTTPException(status_code=500, detail="JSON top-level must be an array")

    return [i for i in dict.fromkeys(ingredients) if i]


# ---------- Main Endpoint: Scan Ingredients ----------
@router.post("/ingredients", response_model=ScanIngredientsResponse)
async def scan_ingredients(file: UploadFile = File(...)):
    """
    Upload an image and use Vertex AI Gemini Vision to detect ingredient names in ENGLISH.
    """
    project_id = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GCP_LOCATION", "us-central1")

    if not project_id:
        raise HTTPException(status_code=500, detail="GCP_PROJECT_ID is not set")

    access_token = _get_vertex_access_token()

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    model = "gemini-2.5-flash"
    url = (
        f"https://{location}-aiplatform.googleapis.com/v1/"
        f"projects/{project_id}/locations/{location}/publishers/google/"
        f"models/{model}:generateContent"
    )

    # ---------- Strong English-only Prompt ----------
    prompt = """
You are an ingredient recognition assistant.

IMPORTANT RULE:
- You MUST output ingredient names ONLY in ENGLISH.
- If the recognized text is in Chinese or any other language, translate it into English.
- No Chinese characters may appear in the output.

TASK:
- Identify ONLY the FOOD INGREDIENTS visible in the image.
- Ignore bowls, plates, background, utensils, packaging, labels, and non-food objects.

OUTPUT FORMAT:
Return ONLY a JSON array of English ingredient names, e.g.:
[
  "mango slices",
  "tapioca pearls",
  "grapefruit pulp"
]

STRICT RULES:
- Output ONLY valid JSON.
- No code blocks.
- No explanations.
- No comments.
- If nothing is detected, return [].
    """.strip()

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {
                        "inlineData": {
                            "mimeType": file.content_type or "image/jpeg",
                            "data": image_b64,
                        }
                    },
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

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=resp.text)

    data = resp.json()

    try:
        reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected Vertex response structure")

    ingredients = _parse_ingredient_names(reply_text)

    return ScanIngredientsResponse(
        ingredients=ingredients,
        ingredients_raw=reply_text,
        raw_vertex=data,
    )