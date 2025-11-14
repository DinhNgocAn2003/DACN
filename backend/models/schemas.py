from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class EventCreate(BaseModel):
    user_id: int
    event_name: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    time_reminder: Optional[int] = None

class TextRequest(BaseModel):
    text: str