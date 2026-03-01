from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CommandLog(BaseModel):
    id: Optional[int] = None
    chat_id: int
    command: str            # e.g. '/set-weather'
    args: Optional[str] = None
    status: str = "ok"      # 'ok' | 'error'
    error_msg: Optional[str] = None
    created_at: Optional[datetime] = None
