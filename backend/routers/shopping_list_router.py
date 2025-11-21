# backend/routers/shopping_list_router.py
import os
import json
from typing import List, Optional

import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.oauth2 import service_account
from google.auth.transport.requests import Request as GoogleAuthRequest


router = APIRouter(prefix="/shopping-list", tags=["Shopping List"])


# ---------- 公共工具（可以和 scan_ingredients_router 复用） ----------
def _get_vertex_access_token() -> str:
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
    去掉 ```json ... ``` / ``` ... ``` 外壳，返回纯 JSON 字符串。
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


# ---------- 数据模型 ----------
class Ingredient(BaseModel):
    name: str
    quantity: Optional[float] = None  # 数量（可以是 1.5、2 等）
    unit: Optional[str] = None        # 单位（g, kg, ml, L, 个, 片, 勺 等）
    notes: Optional[str] = None       # 额外描述：如“大个鸡蛋”“切丁”等


class ShoppingListItem(BaseModel):
    name: str                       # 统一后的购买名称（中文）
    quantity: Optional[float] = None
    unit: Optional[str] = None
    reason: Optional[str] = None    # 简短说明：为什么要买、买多少
    matched_existing: List[str] = []  # 被认为是同类的已有食材名称
    matched_recipe: List[str] = []    # 被认为是同类的菜谱食材名称


class ShoppingListRequest(BaseModel):
    pantry_ingredients: List[Ingredient]
    recipe_ingredients: List[Ingredient]


class ShoppingListResponse(BaseModel):
    to_buy: List[ShoppingListItem]
    shopping_list_raw: str  # 模型原始返回文本（JSON 字符串）
    raw_vertex: dict        # 完整 Vertex 响应（调试用）


# ---------- 主接口：生成购物清单 ----------
@router.post("/generate", response_model=ShoppingListResponse)
async def generate_shopping_list(body: ShoppingListRequest):
    """
    根据【已有食材】和【菜谱所需食材】生成需要购买的购物清单。

    - pantry_ingredients：例如扫描自冰箱/厨房或用户手动输入
    - recipe_ingredients：菜谱生成/解析后的完整用料列表

    Vertex 负责：
    - 识别同一个食材的不同名称（“鸡蛋”“大鸡蛋”“Eggs”等）
    - 合并重复项
    - 按数量对比算出缺口
    - 输出最终需要购买的食材列表
    """
    project_id = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GCP_LOCATION", "us-central1")
    if not project_id:
        raise HTTPException(status_code=500, detail="GCP_PROJECT_ID 未配置")

    access_token = _get_vertex_access_token()

    # 1. 准备模型输入（直接把两个列表作为 JSON 字符串塞给模型）
    pantry_json = body.pantry_ingredients
    recipe_json = body.recipe_ingredients

    # 转成字符串给模型看，方便它做「语义理解 + 数量比较」
    pantry_str = json.dumps([item.dict() for item in pantry_json], ensure_ascii=False)
    recipe_str = json.dumps([item.dict() for item in recipe_json], ensure_ascii=False)

    model = "gemini-2.5-flash"
    url = (
        f"https://{location}-aiplatform.googleapis.com/v1/"
        f"projects/{project_id}/locations/{location}/publishers/google/"
        f"models/{model}:generateContent"
    )

    prompt = f"""
你是一个智能购物清单助手，需要根据“已有食材”和“菜谱所需食材”生成【需要购买】的食材列表。

输入格式：
- pantry_ingredients：用户当前已有的食材列表（JSON 数组）
- recipe_ingredients：菜谱所需的全部食材列表（JSON 数组）
两者的每个元素结构为：
{{
  "name": "食材名称（中文为主，可能包含少量英文）",
  "quantity": 数量 (可以为 null),
  "unit": "单位 (可以为 null)",
  "notes": "可选备注"
}}

请你完成以下工作：
1. 识别“实际是同一种食材”的不同写法或命名，如：
   - "鸡蛋" vs "大鸡蛋" vs "Eggs"
   - "洋葱" vs "紫洋葱"（如果菜谱要求特别指定品种，可以视情况认为是不同）
   - "椰浆" vs "椰奶（罐装）"
   需要你在语义上判断相似度，而不是单纯字符串匹配。

2. 对于每一种菜谱需要的食材：
   - 如果用户【完全没有】对应食材，则应该出现在购物清单中。
   - 如果用户【数量不足】（例如菜谱要 500g，家里只有 200g），则应出现在购物清单中，数量为“缺口数量”（300g）。
   - 如果信息缺失（如某一边没有数量或单位），请基于常识做一个合理但保守的估计，或者只标注“需要补充一些”。

3. 合并重复项：
   - 如果多个菜谱食材被你认为对应同一个购买项目（如“鸡蛋 2 个”和“鸡蛋（大）1 个”），请合并后给出一个统一的购买名称和总缺口数量。
   - 对于被你合并到同一项的原始名称，请在返回结果中用数组记录。

输出格式：
请严格返回一个 JSON 数组（不要任何解释文字），每个元素代表一项“需要购买”的食材，结构为：

[
  {{
    "name": "统一后的购买名称（中文）",
    "quantity": 数量 或 null,
    "unit": "单位 或 null",
    "reason": "简短说明为什么需要购买、以及大概买多少（中文）",
    "matched_existing": ["匹配到的已有食材名称1", "已有食材名称2", ...],
    "matched_recipe": ["匹配到的菜谱食材名称1", "菜谱食材名称2", ...]
  }},
  ...
]

要求：
- 如果完全不需要购买任何东西，请返回 []。
- 只返回 JSON，不要多余解释、不要注释、不要额外字段。
- 字符串请使用中文为主。
    """.strip()

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {"text": "\n\n用户已有食材 pantry_ingredients:\n" + pantry_str},
                    {"text": "\n\n菜谱所需食材 recipe_ingredients:\n" + recipe_str},
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
        raise HTTPException(status_code=500, detail="Unexpected Vertex response")

    # 2. 解析模型输出
    cleaned = _extract_json_from_text(reply_text)
    try:
        raw_list = json.loads(cleaned)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"无法解析 Vertex 购物清单 JSON：{cleaned[:200]}..."
        )

    if not isinstance(raw_list, list):
        raise HTTPException(status_code=500, detail="Vertex 返回的购物清单顶层应为数组")

    to_buy: List[ShoppingListItem] = []
    for item in raw_list:
        if not isinstance(item, dict):
            continue
        to_buy.append(
            ShoppingListItem(
                name=item.get("name", "").strip(),
                quantity=item.get("quantity"),
                unit=item.get("unit"),
                reason=item.get("reason"),
                matched_existing=item.get("matched_existing") or [],
                matched_recipe=item.get("matched_recipe") or [],
            )
        )

    return ShoppingListResponse(
        to_buy=to_buy,
        shopping_list_raw=reply_text,
        raw_vertex=data,
    )