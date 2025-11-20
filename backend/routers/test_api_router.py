# backend/routers/test_api_router.py
import os
import base64
import requests
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

import json
import base64
from google.oauth2 import service_account
from google.auth.transport.requests import Request as GoogleAuthRequest


router = APIRouter(prefix="/test", tags=["Test APIs"])


# --------- DeepSeek 测试 ---------
class DeepSeekTestRequest(BaseModel):
    prompt: str

@router.post("/deepseek")
async def test_deepseek(body: DeepSeekTestRequest):
    """
    简单测试 DeepSeek Chat 接口：
    输入 prompt，返回 DeepSeek 的回复。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="DEEPSEEK_API_KEY 未配置")

    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    ...

    payload = {
        "model": "deepseek-chat",  # 官方文档里的基础 chat 模型 :contentReference[oaicite:0]{index=0}
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": body.prompt},
        ],
        "stream": False,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=resp.text)

    data = resp.json()
    try:
        reply = data["choices"][0]["message"]["content"]
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected DeepSeek response")

    return {
        "prompt": body.prompt,
        "reply": reply,
        "raw": data,  # 方便你调试，后面可以去掉
    }


# backend/routers/test_api_router.py



# ---------- Vertex AI（Gemini）食品识别 ----------
@router.post("/vertex")
async def test_vertex(file: UploadFile = File(...)):
    """
    使用 Google Vertex AI Gemini Vision 对食材进行识别。
    上传图片 → Gemini 模型 → 返回 AI 结构化的原料列表（先返回原始文本）。
    """
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GCP_LOCATION", "us-central1")

    if not cred_path or not project_id:
        raise HTTPException(status_code=500, detail="Google Cloud 环境变量未配置")

    # 1. 用 service account JSON 获取 access token（推荐写法）
    try:
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        creds = service_account.Credentials.from_service_account_file(
            cred_path, scopes=scopes
        )
        creds.refresh(GoogleAuthRequest())
        access_token = creds.token
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取 access token 失败: {e}")

    # 2. 读取并编码图片
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="上传文件为空")

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # 3. 调用 Vertex Gemini 模型（注意模型名带版本号）
    model = "gemini-2.5-flash"
    url = (
        f"https://{location}-aiplatform.googleapis.com/v1/"
        f"projects/{project_id}/locations/{location}/publishers/google/"
        f"models/{model}:generateContent"
    )

    prompt = """
你是食材识别助手。请只关注图中的“食品原料”，忽略餐具、桌面等。
用 JSON 数组输出，每个元素包含：
- name: 食材名称（中文，尽量具体，如“芒果片”“柚子果肉”“椰浆”“西米珍珠”“越南米纸”等）
- category: 大类（水果、乳制品、淀粉类、配料、调味品等）
- confidence: 0~1 之间的置信度（你主观估计即可）

严格只返回 JSON，不要其它解释文字。
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
            "temperature": 0.2,
        },
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        # 直接把 Vertex 返回的错误发给你看
        raise HTTPException(status_code=500, detail=resp.text)

    data = resp.json()

    # 4. 从返回里拿出文本（模型返回的其实是一段字符串形式的 JSON）
    try:
        reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected Vertex response")

    return {
        "ingredients_raw": reply_text,  # 这是模型输出的 JSON 字符串
        "raw": data,                    # 整个 Vertex 响应，方便调试
    }
