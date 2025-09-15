from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


# Simple models chỉ với các fields cần thiết
class SimpleLocation(BaseModel):
    name: str
    country: str
    lat: float
    lon: float
    localtime: str


class SimpleCondition(BaseModel):
    text: str
    code: int


class SimpleCurrent(BaseModel):
    last_updated_epoch: int
    last_updated: str
    temp_c: float
    temp_f: float
    is_day: int
    condition: SimpleCondition
    wind_mph: float
    wind_kph: float
    wind_degree: int
    wind_dir: str
    pressure_mb: float
    pressure_in: float
    precip_mm: float
    precip_in: float
    humidity: int
    cloud: int
    feelslike_c: float
    feelslike_f: float
    vis_km: float
    vis_miles: float
    uv: float
    gust_mph: float
    gust_kph: float
    windchill_c: float
    heatindex_c: float
    dewpoint_c: float
    short_rad: int
    diff_rad: int


class SimpleCurrentResponse(BaseModel):
    location: SimpleLocation
    current: SimpleCurrent


class SimpleForecastDay(BaseModel):
    maxtemp_c: float
    mintemp_c: float
    avgtemp_c: float
    maxwind_mph: float
    maxwind_kph: float
    totalprecip_mm: float
    totalprecip_in: float
    avgvis_km: float
    avgvis_miles: float
    avghumidity: float
    daily_will_it_rain: int
    daily_chance_of_rain: int
    daily_will_it_snow: int
    daily_chance_of_snow: int
    condition: SimpleCondition
    uv: float


class SimpleForecastDayItem(BaseModel):
    date: str
    date_epoch: int
    day: SimpleForecastDay
    astro: Dict[str, Any]  # Flexible for astro data


class SimpleForecast(BaseModel):
    forecastday: List[SimpleForecastDayItem]


class SimpleForecastResponse(BaseModel):
    location: SimpleLocation
    current: SimpleCurrent
    forecast: SimpleForecast


# Request/Response models
class CrawlRequest(BaseModel):
    location: str
    days: Optional[int] = 1
    include_current: bool = True
    include_forecast: bool = False


class CrawlResponse(BaseModel):
    success: bool
    message: str
    location: str
    records_created: int
