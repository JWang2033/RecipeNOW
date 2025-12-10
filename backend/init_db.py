"""Initialize the application's database (create SQLite tables).

Run this after ensuring your environment points to SQLite (no MYSQL_* vars
and no DATABASE_URL), e.g.:

  (venv) python backend/init_db.py

This will import the SQLAlchemy `engine` and `Base` from
`backend.User.database`, import model modules so they register with the
metadata, then call `Base.metadata.create_all(engine)`.
"""
from backend.User.database import engine, Base

# Import models so they are registered on Base.metadata
import backend.User.models.user  # noqa: F401


def init_db():
    Base.metadata.create_all(bind=engine)
    try:
        url = engine.url
    except Exception:
        url = str(engine)
    print("Initialized database for:", url)


if __name__ == "__main__":
    init_db()
