from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Message(BaseModel):
    id: Optional[int] = None
    chat_id: int
    direction: str          # 'in' | 'out'
    content: str
    message_type: str = "text"   # 'text' | 'command' | 'error'
    created_at: Optional[datetime] = None
