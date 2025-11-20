# backend/routers/scan_ingredients_router.py
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
    ingredients_raw: str  # 原始模型返回的文本（一般是 JSON 字符串）
    raw_vertex: dict      # 整个 Vertex 响应，方便调试（上线可以去掉）


# ---------- 内部工具函数 ----------
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
        # 可能是 ```json ... ``` 或 ``` ... ```
        lines = text.splitlines()
        # 去掉第一行 ```xxx
        if len(lines) >= 2 and lines[0].startswith("```"):
            # 找到最后一个 ``` 的行
            if lines[-1].startswith("```"):
                lines = lines[1:-1]
            else:
                lines = lines[1:]
        text = "\n".join(lines).strip()
    return text


def _parse_ingredient_names(reply_text: str) -> List[str]:
    """
    将 Gemini 返回的文本解析为食材名称数组。
    期望格式（示例）：

    [
      "芒果片",
      "柚子果肉",
      "椰浆",
      "西米珍珠"
    ]

    如果你以后改 prompt 为对象形式：
    [
      {"name": "芒果片"},
      {"name": "柚子果肉"}
    ]
    下面也会自动兼容。
    """
    cleaned = _extract_json_from_text(reply_text)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # 解析失败就直接抛错，同时把原始文本一起返回
        raise HTTPException(
            status_code=500,
            detail=f"无法解析 Vertex 返回的 JSON：{cleaned[:200]}..."
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
                # 其他格式暂时忽略
                continue
    else:
        raise HTTPException(
            status_code=500,
            detail="Vertex 返回的 JSON 顶层应为数组"
        )

    # 去重并去掉空串
    ingredients = [i for i in dict.fromkeys(ingredients) if i]

    return ingredients


# ---------- 主接口：扫描图片识别食材名称 ----------
@router.post("/ingredients", response_model=ScanIngredientsResponse)
async def scan_ingredients(file: UploadFile = File(...)):
    """
    上传一张图片，使用 Vertex AI Gemini Vision 识别图片中的“食材名称”，
    只返回识别出来的所有 ingredients 名称列表。
    """
    project_id = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GCP_LOCATION", "us-central1")

    if not project_id:
        raise HTTPException(status_code=500, detail="GCP_PROJECT_ID 未配置")

    # 1. 获取 access token
    access_token = _get_vertex_access_token()

    # 2. 读取并编码图片
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="上传文件为空")

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # 3. 组织 Vertex Gemini 请求
    model = "gemini-2.5-flash"
    url = (
        f"https://{location}-aiplatform.googleapis.com/v1/"
        f"projects/{project_id}/locations/{location}/publishers/google/"
        f"models/{model}:generateContent"
    )

    # 👇 专门为“只返回名称列表”设计的 prompt
    prompt = """
你是一个食材识别助手。请只关注图中的“食品原料”，忽略餐具、餐盘、桌面、装饰品等。

请你返回一个 JSON 数组，数组中的每个元素都是一个字符串，对应一个“食材名称”（中文，尽量具体）。
例如：

[
  "芒果片",
  "柚子果肉",
  "椰浆",
  "西米珍珠",
  "越南米纸"
]

要求：
- 只返回 JSON，不要任何解释文字。
- 不要包含注释或多余字段。
- 如果无法识别任何食材，返回 []。
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

    # 4. 调用 Vertex
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=resp.text)

    data = resp.json()

    # 5. 从返回中取出文本
    try:
        reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected Vertex response")

    # 6. 解析为食材名称数组
    ingredients = _parse_ingredient_names(reply_text)

    return ScanIngredientsResponse(
        ingredients=ingredients,
        ingredients_raw=reply_text,
        raw_vertex=data,
    )
