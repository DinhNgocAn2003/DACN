# db.py
from pathlib import Path
from sqlmodel import Session, create_engine, SQLModel
from typing import Generator

# Compose a proper SQLite URL that works on Windows and other OSes.
BASE_DIR = Path(__file__).parent
DB_FILE = BASE_DIR / "database.db"
DATABASE_URL = f"sqlite:///{DB_FILE.as_posix()}"

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    """Initialize database tables"""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session