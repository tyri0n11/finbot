import httpx
import os
from datetime import datetime
from typing import Optional, List
from models.weatherapi_models import (
    WeatherAPICurrentResponse, 
    WeatherAPIForecastResponse,
    CrawlRequest,
    CrawlResponse
)
from models.weather import WeatherCreate
from services.weather_service import weather_service


class WeatherAPIService:
    def __init__(self):
        self.api_key = os.getenv("WEATHERAPI_KEY", "")
        self.base_url = "http://api.weatherapi.com/v1"
        
    async def get_current_weather(self, location: str) -> Optional[WeatherAPICurrentResponse]:
        """Get current weather data from WeatherAPI.com"""
        url = f"{self.base_url}/current.json"
        params = {
            "key": self.api_key,
            "q": location,
            "aqi": "no"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                return WeatherAPICurrentResponse(**data)
            except Exception as e:
                print(f"Error getting current weather: {e}")
                return None
    
    async def get_forecast_weather(self, location: str, days: int = 1) -> Optional[WeatherAPIForecastResponse]:
        """Get forecast weather data from WeatherAPI.com"""
        url = f"{self.base_url}/forecast.json"
        params = {
            "key": self.api_key,
            "q": location,
            "days": min(days, 10),  # Max 10 days
            "aqi": "no",
            "alerts": "no"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                return WeatherAPIForecastResponse(**data)
            except Exception as e:
                print(f"Error getting forecast weather: {e}")
                return None
    
    def _convert_to_weather_create(self, api_data: WeatherAPICurrentResponse) -> WeatherCreate:
        """Convert WeatherAPI data to our internal Weather model"""
        return WeatherCreate(
            location=f"{api_data.location.name}, {api_data.location.country}",
            temperature=api_data.current.temp_c,
            humidity=api_data.current.humidity,
            pressure=api_data.current.pressure_mb,
            description=api_data.current.condition.get("text", ""),
            wind_speed=api_data.current.wind_kph,
            wind_direction=api_data.current.wind_dir
        )
    
    def _convert_forecast_to_weather_create(self, api_data: WeatherAPIForecastResponse, day_data, hour_data=None) -> WeatherCreate:
        """Convert forecast data to our internal Weather model"""
        if hour_data:
            # Use hourly data if available
            return WeatherCreate(
                location=f"{api_data.location.name}, {api_data.location.country}",
                temperature=hour_data.temp_c,
                humidity=hour_data.humidity,
                pressure=hour_data.pressure_mb,
                description=hour_data.condition.get("text", ""),
                wind_speed=hour_data.wind_kph,
                wind_direction=hour_data.wind_dir
            )
        else:
            # Use daily average data
            return WeatherCreate(
                location=f"{api_data.location.name}, {api_data.location.country}",
                temperature=day_data.day.avgtemp_c,
                humidity=day_data.day.avghumidity,
                pressure=0.0,  # Daily data doesn't have pressure
                description=day_data.day.condition.get("text", ""),
                wind_speed=day_data.day.maxwind_kph,
                wind_direction=""  # Daily data doesn't have wind direction
            )
    
    async def crawl_and_store(self, crawl_request: CrawlRequest) -> CrawlResponse:
        """Crawl weather data and store in ClickHouse"""
        records_created = 0
        
        try:
            # Get current weather if requested
            if crawl_request.include_current:
                current_data = await self.get_current_weather(crawl_request.location)
                if current_data:
                    weather_create = self._convert_to_weather_create(current_data)
                    weather_service.create_weather(weather_create)
                    records_created += 1
            
            # Get forecast weather if requested
            if crawl_request.include_forecast and crawl_request.days > 0:
                forecast_data = await self.get_forecast_weather(crawl_request.location, crawl_request.days)
                if forecast_data:
                    for day_data in forecast_data.forecast.forecastday:
                        # Store daily forecast
                        weather_create = self._convert_forecast_to_weather_create(forecast_data, day_data)
                        weather_service.create_weather(weather_create)
                        records_created += 1
                        
                        # Store hourly forecast (every 6 hours to avoid too much data)
                        for i, hour_data in enumerate(day_data.hour):
                            if i % 6 == 0:  # Every 6 hours
                                weather_create = self._convert_forecast_to_weather_create(forecast_data, day_data, hour_data)
                                weather_service.create_weather(weather_create)
                                records_created += 1
            
            return CrawlResponse(
                success=True,
                message=f"Successfully crawled and stored weather data for {crawl_request.location}",
                location=crawl_request.location,
                records_created=records_created
            )
            
        except Exception as e:
            return CrawlResponse(
                success=False,
                message=f"Error crawling weather data: {str(e)}",
                location=crawl_request.location,
                records_created=records_created
            )


# Global service instance
weatherapi_service = WeatherAPIService()
