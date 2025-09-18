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


# Flat model matching database schema
class WeatherDataFlat(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    city: str
    country: str
    latitude: float
    longitude: float
    localtime: datetime
    last_updated: datetime
    temp_c: float
    temp_f: float
    is_day: int
    condition_text: str
    condition_code: int
    wind_kph: float
    humidity: int
    pressure_mb: float
    precip_mm: float
    feelslike_c: float
    uv: float
    inserted_at: datetime = Field(default_factory=datetime.utcnow)


def parse_weather(data: dict) -> WeatherData:
    return WeatherData(
        location=WeatherLocation(**data["location"]),
        current=WeatherCurrent(
            **{k: v for k, v in data["current"].items() if k != "condition"},
            condition=WeatherCondition(**data["current"]["condition"]),
        ),
    )


def parse_weather_flat(data: dict) -> WeatherDataFlat:
    """Convert nested weather API response to flat structure matching database schema"""
    location = data["location"]
    current = data["current"]
    condition = current["condition"]
    
    return WeatherDataFlat(
        city=location["name"],
        country=location["country"],
        latitude=location["lat"],
        longitude=location["lon"],
        localtime=location["localtime"],
        last_updated=current["last_updated"],
        temp_c=current["temp_c"],
        temp_f=current["temp_f"],
        is_day=current["is_day"],
        condition_text=condition["text"],
        condition_code=condition["code"],
        wind_kph=current["wind_kph"],
        humidity=current["humidity"],
        pressure_mb=current["pressure_mb"],
        precip_mm=current["precip_mm"],
        feelslike_c=current["feelslike_c"],
        uv=current["uv"],
    )