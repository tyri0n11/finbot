import httpx
import os
from datetime import datetime
from typing import Optional, List
from models.weather import WeatherCreate
from services.weather_service import weather_service


class WeatherAPIService:
    def __init__(self):
        self.api_key = os.getenv("WEATHERAPI_KEY", "")
        self.base_url = "http://api.weatherapi.com/v1"
        
    async def get_current_weather_raw(self, location: str) -> Optional[dict]:
        """Get raw current weather data from WeatherAPI.com"""
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
                return response.json()
            except Exception as e:
                print(f"Error getting current weather: {e}")
                return None
    
    async def get_forecast_weather_raw(self, location: str, days: int = 1) -> Optional[dict]:
        """Get raw forecast weather data from WeatherAPI.com"""
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
                return response.json()
            except Exception as e:
                print(f"Error getting forecast weather: {e}")
                return None
    
    def _convert_current_to_weather_create(self, api_data: dict) -> Optional[WeatherCreate]:
        """Convert WeatherAPI current data to our internal Weather model"""
        try:
            location_data = api_data.get("location", {})
            current_data = api_data.get("current", {})
            
            location_name = f"{location_data.get('name', '')}, {location_data.get('country', '')}"
            
            return WeatherCreate(
                location=location_name,
                temperature=current_data.get("temp_c", 0.0),
                humidity=current_data.get("humidity", 0),
                pressure=current_data.get("pressure_mb", 0.0),
                description=current_data.get("condition", {}).get("text", ""),
                wind_speed=current_data.get("wind_kph"),
                wind_direction=current_data.get("wind_dir")
            )
        except Exception as e:
            print(f"Error converting current weather data: {e}")
            return None
    
    def _convert_forecast_day_to_weather_create(self, location_name: str, day_data: dict) -> Optional[WeatherCreate]:
        """Convert forecast day data to our internal Weather model"""
        try:
            day_info = day_data.get("day", {})
            
            return WeatherCreate(
                location=location_name,
                temperature=day_info.get("avgtemp_c", 0.0),
                humidity=day_info.get("avghumidity", 0),
                pressure=0.0,  # Daily data doesn't have pressure
                description=day_info.get("condition", {}).get("text", ""),
                wind_speed=day_info.get("maxwind_kph"),
                wind_direction=""  # Daily data doesn't have wind direction
            )
        except Exception as e:
            print(f"Error converting forecast day data: {e}")
            return None
    
    def _convert_forecast_hour_to_weather_create(self, location_name: str, hour_data: dict) -> Optional[WeatherCreate]:
        """Convert forecast hourly data to our internal Weather model"""
        try:
            return WeatherCreate(
                location=location_name,
                temperature=hour_data.get("temp_c", 0.0),
                humidity=hour_data.get("humidity", 0),
                pressure=hour_data.get("pressure_mb", 0.0),
                description=hour_data.get("condition", {}).get("text", ""),
                wind_speed=hour_data.get("wind_kph"),
                wind_direction=hour_data.get("wind_dir")
            )
        except Exception as e:
            print(f"Error converting hourly weather data: {e}")
            return None
    
    async def crawl_and_store(self, location: str, include_current: bool = True, include_forecast: bool = True, days: int = 3) -> dict:
        """Crawl weather data and store in ClickHouse"""
        records_created = 0
        
        try:
            # Get current weather if requested
            if include_current:
                current_data = await self.get_current_weather_raw(location)
                if current_data:
                    weather_create = self._convert_current_to_weather_create(current_data)
                    if weather_create:
                        weather_service.create_weather(weather_create)
                        records_created += 1
                        print(f"Created current weather record for {location}")
            
            # Get forecast weather if requested
            if include_forecast and days > 0:
                forecast_data = await self.get_forecast_weather_raw(location, days)
                if forecast_data:
                    location_data = forecast_data.get("location", {})
                    location_name = f"{location_data.get('name', '')}, {location_data.get('country', '')}"
                    
                    forecast_days = forecast_data.get("forecast", {}).get("forecastday", [])
                    for day_data in forecast_days:
                        # Store daily forecast
                        weather_create = self._convert_forecast_day_to_weather_create(location_name, day_data)
                        if weather_create:
                            weather_service.create_weather(weather_create)
                            records_created += 1
                            print(f"Created daily forecast record for {location}")
                        
                        # Store hourly forecast (every 6 hours to avoid too much data)
                        hourly_data = day_data.get("hour", [])
                        for i, hour_data in enumerate(hourly_data):
                            if i % 6 == 0:  # Every 6 hours
                                weather_create = self._convert_forecast_hour_to_weather_create(location_name, hour_data)
                                if weather_create:
                                    weather_service.create_weather(weather_create)
                                    records_created += 1
                                    print(f"Created hourly forecast record for {location} at {hour_data.get('time')}")
            
            return {
                "success": True,
                "message": f"Successfully crawled and stored weather data for {location}",
                "location": location,
                "records_created": records_created
            }
            
        except Exception as e:
            print(f"Error in crawl_and_store: {e}")
            return {
                "success": False,
                "message": f"Error crawling weather data: {str(e)}",
                "location": location,
                "records_created": records_created
            }


# Global service instance
weatherapi_service = WeatherAPIService()
