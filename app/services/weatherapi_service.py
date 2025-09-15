import httpx
import os
from datetime import datetime, date, timedelta
from typing import List, Optional
from models.weatherapi import (
    WeatherAPICurrentResponse, 
    WeatherAPIForecastResponse, 
    WeatherAPIHistoryResponse,
    WeatherAPISearchResult
)
from models.weather import WeatherCreate
from services.weather_service import weather_service


class WeatherAPIService:
    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "http://api.weatherapi.com/v1"
        
        if not self.api_key:
            raise ValueError("WEATHER_API_KEY environment variable is required")
    
    async def get_current_weather(self, location: str) -> WeatherAPICurrentResponse:
        """Get current weather for a location"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/current.json",
                params={
                    "key": self.api_key,
                    "q": location,
                    "aqi": "no"
                }
            )
            response.raise_for_status()
            data = response.json()
            return WeatherAPICurrentResponse(**data)
    
    async def get_forecast(self, location: str, days: int = 1, aqi: bool = False, alerts: bool = False) -> WeatherAPIForecastResponse:
        """Get weather forecast for a location (up to 14 days)"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/forecast.json",
                params={
                    "key": self.api_key,
                    "q": location,
                    "days": min(days, 14),  # Max 14 days
                    "aqi": "yes" if aqi else "no",
                    "alerts": "yes" if alerts else "no"
                }
            )
            response.raise_for_status()
            data = response.json()
            return WeatherAPIForecastResponse(**data)
    
    async def get_history(self, location: str, dt: date) -> WeatherAPIHistoryResponse:
        """Get historical weather for a location and date"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/history.json",
                params={
                    "key": self.api_key,
                    "q": location,
                    "dt": dt.strftime("%Y-%m-%d")
                }
            )
            response.raise_for_status()
            data = response.json()
            return WeatherAPIHistoryResponse(**data)
    
    async def search_locations(self, query: str) -> List[WeatherAPISearchResult]:
        """Search for locations"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search.json",
                params={
                    "key": self.api_key,
                    "q": query
                }
            )
            response.raise_for_status()
            data = response.json()
            return [WeatherAPISearchResult(**item) for item in data]
    
    def _convert_to_local_weather(self, weather_data: WeatherAPICurrentResponse) -> WeatherCreate:
        """Convert WeatherAPI data to local weather format"""
        current = weather_data.current
        location = weather_data.location
        
        return WeatherCreate(
            location=f"{location.name}, {location.region}, {location.country}",
            temperature=current.temp_c,
            humidity=current.humidity,
            pressure=current.pressure_mb,
            description=current.condition.text,
            wind_speed=current.wind_kph,
            wind_direction=current.wind_dir
        )
    
    async def crawl_and_save_current_weather(self, location: str) -> dict:
        """Crawl current weather from WeatherAPI and save to local database"""
        try:
            # Get current weather from WeatherAPI
            weather_data = await self.get_current_weather(location)
            
            # Convert to local format
            local_weather = self._convert_to_local_weather(weather_data)
            
            # Save to local database
            saved_weather = weather_service.create_weather(local_weather)
            
            return {
                "status": "success",
                "message": f"Weather data for {location} saved successfully",
                "data": saved_weather.dict(),
                "source": "WeatherAPI.com"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to crawl weather data: {str(e)}",
                "location": location
            }
    
    async def crawl_forecast_and_save(self, location: str, days: int = 7) -> dict:
        """Crawl forecast weather and save to database"""
        try:
            forecast_data = await self.get_forecast(location, days)
            saved_records = []
            
            for forecast_day in forecast_data.forecast.forecastday:
                # Save daily average
                day_data = forecast_day.day
                daily_weather = WeatherCreate(
                    location=f"{forecast_data.location.name}, {forecast_data.location.region}, {forecast_data.location.country}",
                    temperature=day_data.avgtemp_c,
                    humidity=day_data.avghumidity,
                    pressure=0,  # Not available in daily forecast
                    description=day_data.condition.text,
                    wind_speed=day_data.maxwind_kph,
                    wind_direction=""  # Not available in daily forecast
                )
                
                saved_record = weather_service.create_weather(daily_weather)
                saved_records.append(saved_record.dict())
            
            return {
                "status": "success",
                "message": f"Forecast data for {location} ({days} days) saved successfully",
                "records_count": len(saved_records),
                "data": saved_records,
                "source": "WeatherAPI.com"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to crawl forecast data: {str(e)}",
                "location": location
            }
    
    async def crawl_history_and_save(self, location: str, start_date: date, end_date: date) -> dict:
        """Crawl historical weather data and save to database"""
        try:
            saved_records = []
            current_date = start_date
            
            while current_date <= end_date:
                try:
                    history_data = await self.get_history(location, current_date)
                    
                    for forecast_day in history_data.forecast.forecastday:
                        day_data = forecast_day.day
                        daily_weather = WeatherCreate(
                            location=f"{history_data.location.name}, {history_data.location.region}, {history_data.location.country}",
                            temperature=day_data.avgtemp_c,
                            humidity=day_data.avghumidity,
                            pressure=0,  # Not available in daily data
                            description=day_data.condition.text,
                            wind_speed=day_data.maxwind_kph,
                            wind_direction=""
                        )
                        
                        saved_record = weather_service.create_weather(daily_weather)
                        saved_records.append(saved_record.dict())
                
                except Exception as e:
                    print(f"Failed to get history for {current_date}: {e}")
                
                current_date += timedelta(days=1)
            
            return {
                "status": "success",
                "message": f"Historical data for {location} from {start_date} to {end_date} saved successfully",
                "records_count": len(saved_records),
                "data": saved_records,
                "source": "WeatherAPI.com"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to crawl historical data: {str(e)}",
                "location": location
            }


# Global service instance
weather_api_service = WeatherAPIService()
