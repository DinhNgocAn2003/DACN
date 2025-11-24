from pathlib import Path
from sqlmodel import Session, create_engine, SQLModel
from typing import Generator

# Tạo URL SQLite phù hợp cho Windows và các hệ điều hành khác
BASE_DIR = Path(__file__).parent
DB_FILE = BASE_DIR / "database.db"
DATABASE_URL = f"sqlite:///{DB_FILE.as_posix()}"

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    #Khởi tạo các bảng trong database.
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    # Trả về Context-managed session để sử dụng trong các route
    with Session(engine) as session:
        yield session