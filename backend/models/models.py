# models.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, String


class User(SQLModel, table=True):
    """Model mapped to existing `users` table in the DB.

    The database currently stores the password in a column named `password`.
    To keep the API using the attribute name `password_hash`, map that
    attribute to the `password` column via `sa_column`.
    """
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password_hash: str = Field(sa_column=Column("password", String))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_verified: int = 0


class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: Optional[int] = Field(default=None, primary_key=True)
    # foreign key points to `users.id` in the DB (plural table)
    user_id: int = Field(foreign_key="users.id")
    event_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    time_reminder: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
