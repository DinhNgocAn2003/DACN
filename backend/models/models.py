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
    # `is_verified` column was removed from the users table; keep model minimal.


class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: Optional[int] = Field(default=None, primary_key=True)
    # foreign key points to `users.id` in the DB (plural table)
    user_id: int = Field(foreign_key="users.id")
    event_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    # time_reminder stored as minutes before start_time (integer). If None, no reminder.
    time_reminder: Optional[int] = None
    # reminder_sent indicates whether the reminder email was already sent
    reminder_sent: bool = False
    reminder_sent_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
