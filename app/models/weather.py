from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class WeatherBase(BaseModel):
    location: str
    temperature: float
    humidity: float
    pressure: float
    description: str
    wind_speed: Optional[float] = None
    wind_direction: Optional[str] = None


class WeatherCreate(WeatherBase):
    pass


class WeatherUpdate(BaseModel):
    location: Optional[str] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    description: Optional[str] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[str] = None


class WeatherResponse(WeatherBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
