"""Initialize the application's database (create SQLite tables).

Run this after ensuring your environment points to SQLite (no MYSQL_* vars
and no DATABASE_URL), e.g.:

  (venv) python backend/init_db.py

This will import the SQLAlchemy `engine` and `Base` from
`backend.User.database`, import model modules so they register with the
metadata, then call `Base.metadata.create_all(engine)`.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.User.database import engine, Base

# Import models so they are registered on Base.metadata
import backend.User.models.user  # noqa: F401
import backend.User.models.pantry_item  # noqa: F401
import backend.User.models.preferences  # noqa: F401


def init_db():
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    try:
        url = engine.url
    except Exception:
        url = str(engine)
    print(f"✅ 数据库初始化完成！")
    print(f"数据库连接: {url}")

    # 打印创建的表
    print("\n创建的表:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")


if __name__ == "__main__":
    init_db()
