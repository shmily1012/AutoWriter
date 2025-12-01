from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from novel_system.backend.core.config import get_settings

settings = get_settings()

# Cast PostgresDsn to str to keep SQLAlchemy happy.
engine = create_engine(str(settings.postgres_dsn))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

__all__ = ["engine", "SessionLocal"]
