# backend/User/utils/security.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt
import bcrypt  # 直接使用 bcrypt 模块，而不是 passlib


# =========================
# 🔐 bcrypt 相关工具函数
# =========================

def _normalize_password(password: str) -> bytes:
    """
    bcrypt 只会安全处理前 72 bytes 的密码，这里统一做：
    - 转为 UTF-8 bytes
    - 超过 72 bytes 的部分截断
    返回 bytes，供 hash / check 使用。
    """
    if password is None:
        password = ""
    pw_bytes = password.encode("utf-8")
    if len(pw_bytes) > 72:
        pw_bytes = pw_bytes[:72]
    return pw_bytes


def get_password_hash(password: str) -> str:
    """
    使用 bcrypt 生成密码哈希。
    返回 str（UTF-8 解码后的哈希串），用于存入数据库。
    """
    pw_bytes = _normalize_password(password)
    hashed: bytes = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    校验明文密码是否匹配数据库中的 bcrypt 哈希。
    """
    pw_bytes = _normalize_password(plain_password)

    if isinstance(hashed_password, str):
        hashed_bytes = hashed_password.encode("utf-8")
    else:
        hashed_bytes = hashed_password

    try:
        return bcrypt.checkpw(pw_bytes, hashed_bytes)
    except ValueError:
        # 如果 hashed_password 不是有效的 bcrypt hash
        return False


# =========================
# 🔑 JWT 相关配置
# =========================

# ⚠ 生产环境请换成环境变量，并使用随机强密钥
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # token 有效期（分钟）


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建 JWT access token。
    data: 会被放入 JWT payload，例如 {"sub": user.phone_number, "role": "user"}
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解码并验证 JWT。验证失败时返回 None。
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
