from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: Optional[int] = None
    chat_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    language: str = "vi"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
