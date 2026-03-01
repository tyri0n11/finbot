from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserSubscription(BaseModel):
    id: Optional[int] = None
    chat_id: int
    subscription_type: str  # 'weather' | 'news' | 'gold_price'
    scheduled_time: str     # 'HH:MM' 24h format
    frequency: str = "daily"
    is_active: bool = True
    last_sent_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
