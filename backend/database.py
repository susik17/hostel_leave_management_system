from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings

settings = get_settings()
# Use absolute path for default SQLite so it works regardless of CWD
db_url = settings.database_url
if db_url == "sqlite:///./hostel_leave.db" or db_url.startswith("sqlite:///./"):
    backend_dir = Path(__file__).resolve().parent
    db_path = backend_dir / "hostel_leave.db"
    db_url = f"sqlite:///{db_path.as_posix()}"
# SQLite needs connect_args for threading
connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}
engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
