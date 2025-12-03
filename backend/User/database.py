from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.User.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


# ✅ 添加这个函数以供依赖注入使用
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()