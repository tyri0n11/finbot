from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class WeatherAPILocation(BaseModel):
    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str = Field(alias="tz_id")
    localtime_epoch: int
    localtime: str


class WeatherAPICondition(BaseModel):
    text: Optional[str] = None
    icon: Optional[str] = None
    code: int


class WeatherAPICurrent(BaseModel):
    last_updated_epoch: int
    last_updated: str
    temp_c: float
    temp_f: float
    is_day: int
    condition: WeatherAPICondition
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
    vis_km: float
    vis_miles: float
    uv: float
    gust_mph: float
    gust_kph: float
    short_rad: Optional[float] = None
    diff_rad: Optional[float] = None
    dni: Optional[float] = None
    gti: Optional[float] = None


class WeatherAPICurrentResponse(BaseModel):
    location: WeatherAPILocation
    current: WeatherAPICurrent


# Forecast Models
class WeatherAPIDay(BaseModel):
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
    condition: WeatherAPICondition
    uv: float


class WeatherAPIAstro(BaseModel):
    sunrise: str
    sunset: str
    moonrise: str
    moonset: str
    moon_phase: str
    moon_illumination: int
    is_moon_up: int
    is_sun_up: int


class WeatherAPIHour(BaseModel):
    time_epoch: Optional[int] = None
    time: Optional[str] = None
    temp_c: Optional[float] = None
    temp_f: Optional[float] = None
    is_day: Optional[int] = None
    condition: Optional[WeatherAPICondition] = None
    wind_mph: Optional[float] = None
    wind_kph: Optional[float] = None
    wind_degree: Optional[int] = None
    wind_dir: Optional[str] = None
    pressure_mb: Optional[float] = None
    pressure_in: Optional[float] = None
    precip_mm: Optional[float] = None
    precip_in: Optional[float] = None
    snow_cm: Optional[float] = None
    humidity: Optional[int] = None
    cloud: Optional[int] = None
    feelslike_c: Optional[float] = None
    feelslike_f: Optional[float] = None
    windchill_c: Optional[float] = None
    windchill_f: Optional[float] = None
    heatindex_c: Optional[float] = None
    heatindex_f: Optional[float] = None
    dewpoint_c: Optional[float] = None
    dewpoint_f: Optional[float] = None
    will_it_rain: Optional[int] = None
    chance_of_rain: Optional[int] = None
    will_it_snow: Optional[int] = None
    chance_of_snow: Optional[int] = None
    vis_km: Optional[float] = None
    vis_miles: Optional[float] = None
    gust_mph: Optional[float] = None
    gust_kph: Optional[float] = None
    uv: Optional[float] = None
    short_rad: Optional[float] = None
    diff_rad: Optional[float] = None
    dni: Optional[float] = None
    gti: Optional[float] = None


class WeatherAPIForecastDay(BaseModel):
    date: str
    date_epoch: int
    day: WeatherAPIDay
    astro: WeatherAPIAstro
    hour: List[WeatherAPIHour]


class WeatherAPIForecast(BaseModel):
    forecastday: List[WeatherAPIForecastDay]


class WeatherAPIForecastResponse(BaseModel):
    location: WeatherAPILocation
    current: WeatherAPICurrent
    forecast: WeatherAPIForecast


# History Models
class WeatherAPIHistoryResponse(BaseModel):
    location: WeatherAPILocation
    forecast: WeatherAPIForecast  # History uses same structure as forecast


# Search Models
class WeatherAPISearchResult(BaseModel):
    id: int
    name: str
    region: str
    country: str
    lat: float
    lon: float
    url: str


# Error Models
class WeatherAPIError(BaseModel):
    code: int
    message: str
