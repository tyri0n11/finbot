from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field


class WeatherCondition(BaseModel):
    text: str
    code: int


class WeatherCurrent(BaseModel):
    last_updated: datetime
    temp_c: float
    temp_f: float
    is_day: int
    condition: WeatherCondition
    wind_kph: float
    humidity: int
    pressure_mb: float
    precip_mm: float
    feelslike_c: float
    uv: float


class WeatherLocation(BaseModel):
    name: str
    country: str
    lat: float
    lon: float
    localtime: datetime


class WeatherData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    location: WeatherLocation
    current: WeatherCurrent
    inserted_at: datetime = Field(default_factory=datetime.utcnow)


def parse_weather(data: dict) -> WeatherData:
    return WeatherData(
        location=WeatherLocation(**data["location"]),
        current=WeatherCurrent(
            **{k: v for k, v in data["current"].items() if k != "condition"},
            condition=WeatherCondition(**data["current"]["condition"]),
        ),
    )