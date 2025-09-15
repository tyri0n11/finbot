from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class WeatherAPILocation(BaseModel):
    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str
    localtime_epoch: int
    localtime: str


class WeatherAPICurrent(BaseModel):
    last_updated_epoch: int
    last_updated: str
    temp_c: float
    temp_f: float
    is_day: int
    condition: dict
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


class WeatherAPICurrentResponse(BaseModel):
    location: WeatherAPILocation
    current: WeatherAPICurrent


class WeatherAPIForecastDay(BaseModel):
    maxtemp_c: float
    maxtemp_f: float
    mintemp_c: float
    mintemp_f: float
    avgtemp_c: float
    avgtemp_f: float
    maxwind_mph: float
    maxwind_kph: float
    totalprecip_mm: float
    totalprecip_in: float
    totalsnow_cm: float
    avgvis_km: float
    avgvis_miles: float
    avghumidity: float
    daily_will_it_rain: int
    daily_chance_of_rain: int
    daily_will_it_snow: int
    daily_chance_of_snow: int
    condition: dict
    uv: float


class WeatherAPIForecastHour(BaseModel):
    time_epoch: int
    time: str
    temp_c: float
    temp_f: float
    is_day: int
    condition: dict
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
    windchill_c: float
    windchill_f: float
    heatindex_c: float
    heatindex_f: float
    dewpoint_c: float
    dewpoint_f: float
    will_it_rain: int
    chance_of_rain: int
    will_it_snow: int
    chance_of_snow: int
    vis_km: float
    vis_miles: float
    gust_mph: float
    gust_kph: float
    uv: float


class WeatherAPIForecastDayItem(BaseModel):
    date: str
    date_epoch: int
    day: WeatherAPIForecastDay
    astro: dict
    hour: List[WeatherAPIForecastHour]


class WeatherAPIForecast(BaseModel):
    forecastday: List[WeatherAPIForecastDayItem]


class WeatherAPIForecastResponse(BaseModel):
    location: WeatherAPILocation
    current: WeatherAPICurrent
    forecast: WeatherAPIForecast


# Request models for automation engine
class CrawlRequest(BaseModel):
    location: str
    days: Optional[int] = 1  # For forecast (1-10 days)
    include_current: bool = True
    include_forecast: bool = False


class CrawlResponse(BaseModel):
    success: bool
    message: str
    location: str
    records_created: int
