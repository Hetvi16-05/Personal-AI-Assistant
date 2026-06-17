from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# psycopg v2 uses postgresql+psycopg2:// dialect
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://") or db_url.startswith("postgres://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)

engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables (used for local SQLite fallback only)."""
    from app.models import user, goal, project, task, memory, roadmap, report, chat, vector_memory, insight  # noqa
    Base.metadata.create_all(bind=engine)
