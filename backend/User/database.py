# backend/User/database.py

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载根目录 .env
load_dotenv()

# 默认使用项目 data 文件夹中的 SQLite
BASE_DIR = Path(__file__).resolve().parents[2]
default_sqlite_path = BASE_DIR / "data"
default_sqlite_path.mkdir(parents=True, exist_ok=True)
default_sqlite_url = f"sqlite:///{default_sqlite_path / 'recipenow.db'}"

env_database_url = os.getenv("DATABASE_URL")
mysql_env_present = any(
    os.getenv(key) is not None
    for key in ["MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_HOST", "MYSQL_PORT", "MYSQL_DB"]
)

if env_database_url:
    SQLALCHEMY_DATABASE_URL = env_database_url
elif mysql_env_present:
    MYSQL_USER = os.getenv("MYSQL_USER", "user")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "recipenow")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3309")
    MYSQL_DB = os.getenv("MYSQL_DB", "recipenow")
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
else:
    SQLALCHEMY_DATABASE_URL = default_sqlite_url

# -------------------------
# SQLAlchemy 初始化
# -------------------------
engine_kwargs = {"pool_pre_ping": True}
url_obj = make_url(SQLALCHEMY_DATABASE_URL)
if url_obj.drivername == "sqlite":
    if url_obj.database:
        Path(url_obj.database).parent.mkdir(parents=True, exist_ok=True)
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


# -------------------------
# FastAPI 用的依赖函数 get_db()
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
