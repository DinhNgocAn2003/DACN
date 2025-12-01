# models.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, String


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password_hash: str = Field(sa_column=Column("password", String))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: Optional[int] = Field(default=None, primary_key=True)
# khóa ngoại trỏ đến `users.id` trong cơ sở dữ liệu
    user_id: int = Field(foreign_key="users.id")
    event_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
# time_reminder được lưu dưới dạng phút trước start_time (số nguyên). Nếu là None, không có nhắc nhở.
    time_reminder: Optional[int] = None
# reminder_sent cho biết liệu email nhắc nhở đã được gửi hay chưa
    reminder_sent: bool = False
    reminder_sent_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
