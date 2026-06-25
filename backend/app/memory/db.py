from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.memory.models import Base


def _build_engine():
    settings = get_settings()
    is_sqlite = settings.database_url.startswith("sqlite")
    if is_sqlite:
        db_path = settings.database_url.split("///")[-1]
        Path(db_path).resolve().parent.mkdir(parents=True, exist_ok=True)

    connect_args = {"check_same_thread": False} if is_sqlite else {}
    return create_engine(settings.database_url, connect_args=connect_args)


engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(engine)


def get_db() -> Session:
    return SessionLocal()
