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
    ingredients: List[str]   # 输入的食材列表（回显）
    recipe_raw: str          # 模型生成的菜谱文本（JSON 字符串）
    raw_vertex: dict         # 整个 Vertex 响应，方便调试（上线可以去掉）


# ---------- 内部工具函数（调用格式与 scan_router 保持一致） ----------
def _get_vertex_access_token() -> str:
    """
    使用 Service Account JSON 获取 Google Cloud 的 access token。
    依赖环境变量：
    - GOOGLE_APPLICATION_CREDENTIALS
    """
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise HTTPException(status_code=500, detail="GOOGLE_APPLICATION_CREDENTIALS 未配置")

    try:
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        creds = service_account.Credentials.from_service_account_file(
            cred_path, scopes=scopes
        )
        creds.refresh(GoogleAuthRequest())
        return creds.token
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取 Google access token 失败: {e}")


def _extract_json_from_text(text: str) -> str:
    """
    模型有时会用 ```json ... ``` 或 ``` 包裹输出，这里做一次清洗，
    返回纯 JSON 字符串。
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


# ---------- 主接口：根据食材生成菜谱 ----------
@router.post("/ingredients", response_model=GenerateRecipeResponse)
async def generate_recipe_from_ingredients(body: GenerateRecipeRequest):
    """
    基于 scan_router 返回的食材列表，使用 Vertex AI Gemini 生成菜谱。

    调用格式：
      POST /generate/ingredients
      Body (JSON):
      {
        "ingredients": ["鸡胸肉", "西兰花", "橄榄油", "大蒜"]
      }
    """
    project_id = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GCP_LOCATION", "us-central1")

    if not project_id:
        raise HTTPException(status_code=500, detail="GCP_PROJECT_ID 未配置")

    # 1. 获取 access token（调用方式与 scan_router 完全一致）
    access_token = _get_vertex_access_token()

    # 2. 组织 Vertex Gemini 请求
    model = "gemini-2.5-flash"
    url = (
        f"https://{location}-aiplatform.googleapis.com/v1/"
        f"projects/{project_id}/locations/{location}/publishers/google/"
        f"models/{model}:generateContent"
    )

    # 把 ingredients 列表拼成一个字符串，放进 Prompt 中
    ingredients_list_str = ", ".join(body.ingredients) if body.ingredients else "（无食材）"

    prompt = f"""
你是一名专业的家庭料理食谱助手。现在给你一组可用的食材，请你基于这些食材设计一道适合家庭制作的菜谱。

可用食材列表（中文）：{ingredients_list_str}

要求：
1. 优先使用上述食材，如果必须新增少量基础调味料（如盐、糖、酱油、胡椒等）是可以的，但不要加入完全无关的复杂食材。
2. 生成的菜谱应为一整道菜，而不是多道菜的合集。
3. 菜谱适合 1–2 人份的日常食用，烹饪步骤不要过于复杂。

请以 **JSON 格式** 输出菜谱信息，结构如下（示例）：

{{
  "title": "蒜香西兰花鸡胸肉",
  "servings": 2,
  "ingredients": [
    {{
      "name": "鸡胸肉",
      "amount": 200,
      "unit": "克"
    }},
    {{
      "name": "西兰花",
      "amount": 150,
      "unit": "克"
    }},
    {{
      "name": "大蒜",
      "amount": 3,
      "unit": "瓣"
    }},
    {{
      "name": "橄榄油",
      "amount": 1,
      "unit": "汤匙"
    }},
    {{
      "name": "盐",
      "amount": 1,
      "unit": "茶匙"
    }}
  ],
  "steps": [
    "步骤1：处理食材……",
    "步骤2：加热锅，倒入橄榄油……",
    "步骤3：加入鸡胸肉翻炒至变色……",
    "步骤4：加入西兰花和调味料，翻炒至熟……"
  ],
  "estimated_time_minutes": 25,
  "difficulty": "简单"
}}

字段说明：
- title: 菜名（中文）
- servings: 份数（整数）
- ingredients: 数组，每个元素包含 name（食材名）、amount（数量，数字）、unit（单位，如 克、毫升、汤匙、茶匙 等）
- steps: 字符串数组，每个元素是一条清晰的步骤说明
- estimated_time_minutes: 预计总耗时（分钟，整数）
- difficulty: 难度（例如："简单"、"中等"、"稍有难度"）

注意：
- 严格只返回 JSON，不要额外的解释性文字。
- 不要使用注释或多余字段。
    """.strip()

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.6,  # 比较有创意一点
        },
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    # 3. 调用 Vertex（调用方式与 scan_router 完全一致）
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=resp.text)

    data = resp.json()

    # 4. 从返回中提取文本
    try:
        reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected Vertex response")

    # 5. 清洗可能的 ```json 包裹，保持与 scan_router 的处理风格一致
    cleaned_recipe_json = _extract_json_from_text(reply_text)

    # 可选：这里可以尝试 json.loads(cleaned_recipe_json) 校验是否合法，
    # 如果你希望接口在 JSON 不合法时直接报错。
    try:
        json.loads(cleaned_recipe_json)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"Vertex 返回的菜谱不是合法 JSON：{cleaned_recipe_json[:200]}..."
        )

    return GenerateRecipeResponse(
        ingredients=body.ingredients,
        recipe_raw=cleaned_recipe_json,
        raw_vertex=data,
    )