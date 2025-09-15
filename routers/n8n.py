from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from models.weather import WeatherResponse
from services.weather_service import weather_service

router = APIRouter(prefix="/n8n", tags=["n8n"])


class TelegramWeatherResponse(BaseModel):
    """Formatted response for Telegram bot via N8N"""
    location: str
    current_temp: float
    description: str
    humidity: int
    pressure: float
    wind_speed: Optional[float]
    wind_direction: Optional[str]
    last_updated: datetime
    message: str  # Formatted message for Telegram


class TelegramForecastResponse(BaseModel):
    """Forecast data formatted for Telegram"""
    location: str
    forecast_days: int
    forecast_data: List[dict]
    message: str  # Formatted message for Telegram


@router.get("/weather/current/{location}", response_model=TelegramWeatherResponse)
async def get_current_weather_for_telegram(location: str):
    """
    Get latest weather data for a location formatted for Telegram bot
    N8N will call this endpoint to get weather data for sending to Telegram
    """
    try:
        # Get latest weather records for this location
        weather_records = weather_service.get_weather_by_location(location, limit=1)
        
        if not weather_records:
            raise HTTPException(status_code=404, detail=f"No weather data found for {location}")
        
        latest_record = weather_records[0]
        
        # Format message for Telegram
        message = f"""🌤 **Weather Update for {latest_record.location}**

🌡️ Temperature: {latest_record.temperature}°C
📝 Condition: {latest_record.description}
💧 Humidity: {latest_record.humidity}%
🎈 Pressure: {latest_record.pressure} mb"""

        if latest_record.wind_speed:
            message += f"\n💨 Wind: {latest_record.wind_speed} km/h"
            if latest_record.wind_direction:
                message += f" {latest_record.wind_direction}"

        message += f"\n🕐 Last Updated: {latest_record.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"
        
        return TelegramWeatherResponse(
            location=latest_record.location,
            current_temp=latest_record.temperature,
            description=latest_record.description,
            humidity=int(latest_record.humidity),
            pressure=latest_record.pressure,
            wind_speed=latest_record.wind_speed,
            wind_direction=latest_record.wind_direction,
            last_updated=latest_record.updated_at,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather data: {str(e)}")


@router.get("/weather/forecast/{location}", response_model=TelegramForecastResponse)
async def get_weather_forecast_for_telegram(
    location: str,
    days: int = Query(3, ge=1, le=7, description="Number of forecast days")
):
    """
    Get weather forecast formatted for Telegram bot
    """
    try:
        # Get recent weather records that might include forecast data
        weather_records = weather_service.get_weather_by_location(location, limit=days * 4)
        
        if not weather_records:
            raise HTTPException(status_code=404, detail=f"No forecast data found for {location}")
        
        # Group by date and take representative data
        forecast_data = []
        current_date = None
        daily_records = []
        
        for record in weather_records:
            record_date = record.created_at.date()
            
            if current_date != record_date:
                if daily_records:
                    # Process previous day's data
                    avg_temp = sum(r.temperature for r in daily_records) / len(daily_records)
                    forecast_data.append({
                        "date": current_date.strftime("%Y-%m-%d"),
                        "temperature": round(avg_temp, 1),
                        "description": daily_records[0].description,
                        "humidity": daily_records[0].humidity,
                        "pressure": daily_records[0].pressure
                    })
                
                current_date = record_date
                daily_records = [record]
            else:
                daily_records.append(record)
        
        # Process last day's data
        if daily_records:
            avg_temp = sum(r.temperature for r in daily_records) / len(daily_records)
            forecast_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "temperature": round(avg_temp, 1),
                "description": daily_records[0].description,
                "humidity": daily_records[0].humidity,
                "pressure": daily_records[0].pressure
            })
        
        # Limit to requested days
        forecast_data = forecast_data[:days]
        
        # Format message for Telegram
        message = f"📅 **{days}-Day Weather Forecast for {location}**\n\n"
        
        for day_data in forecast_data:
            message += f"📆 **{day_data['date']}**\n"
            message += f"🌡️ {day_data['temperature']}°C - {day_data['description']}\n"
            message += f"💧 Humidity: {day_data['humidity']}%\n\n"
        
        return TelegramForecastResponse(
            location=location,
            forecast_days=len(forecast_data),
            forecast_data=forecast_data,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get forecast data: {str(e)}")


@router.get("/weather/summary/{location}")
async def get_weather_summary_for_telegram(location: str):
    """
    Get weather summary with both current and forecast data
    """
    try:
        current_response = await get_current_weather_for_telegram(location)
        forecast_response = await get_weather_forecast_for_telegram(location, days=3)
        
        combined_message = current_response.message + "\n\n" + forecast_response.message
        
        return {
            "location": location,
            "current": current_response,
            "forecast": forecast_response,
            "combined_message": combined_message
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather summary: {str(e)}")


@router.get("/locations")
async def get_available_locations():
    """
    Get list of locations that have weather data
    Useful for N8N to know which locations are available
    """
    try:
        # Get recent weather records and extract unique locations
        recent_records = weather_service.get_weather_list(limit=1000)
        locations = list(set(record.location for record in recent_records))
        
        return {
            "locations": sorted(locations),
            "total": len(locations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get locations: {str(e)}")
