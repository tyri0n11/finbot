from datetime import date, datetime, timedelta
from typing import List
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from services.weatherapi_service import weather_api_service

router = APIRouter(prefix="/crawl", tags=["weather-crawling"])


class CrawlResponse(BaseModel):
    status: str
    message: str
    location: str = None
    records_count: int = None
    source: str = "WeatherAPI.com"


@router.post("/current/{location}", response_model=dict)
async def crawl_current_weather(location: str):
    """Crawl current weather for a location and save to database"""
    try:
        result = await weather_api_service.crawl_and_save_current_weather(location)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to crawl current weather: {str(e)}")


@router.post("/forecast/{location}", response_model=dict)
async def crawl_forecast_weather(
    location: str,
    days: int = Query(default=7, ge=1, le=14, description="Number of forecast days (1-14)")
):
    """Crawl weather forecast for a location and save to database"""
    try:
        result = await weather_api_service.crawl_forecast_and_save(location, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to crawl forecast weather: {str(e)}")


@router.post("/history/{location}", response_model=dict)
async def crawl_historical_weather(
    location: str,
    start_date: date = Query(description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(description="End date (YYYY-MM-DD)")
):
    """Crawl historical weather for a location and date range"""
    # Validate date range
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date")
    
    # Limit to prevent too many API calls
    if (end_date - start_date).days > 30:
        raise HTTPException(status_code=400, detail="Date range cannot exceed 30 days")
    
    if start_date > date.today():
        raise HTTPException(status_code=400, detail="Start date cannot be in the future")
    
    try:
        result = await weather_api_service.crawl_history_and_save(location, start_date, end_date)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to crawl historical weather: {str(e)}")


@router.post("/batch-current", response_model=dict)
async def crawl_batch_current_weather(
    locations: List[str],
    background_tasks: BackgroundTasks
):
    """Crawl current weather for multiple locations (background task)"""
    if len(locations) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 locations allowed per batch")
    
    async def process_batch():
        results = []
        for location in locations:
            try:
                result = await weather_api_service.crawl_and_save_current_weather(location)
                results.append(result)
            except Exception as e:
                results.append({
                    "status": "error",
                    "message": str(e),
                    "location": location
                })
        return results
    
    background_tasks.add_task(process_batch)
    
    return {
        "status": "accepted",
        "message": f"Batch crawling started for {len(locations)} locations",
        "locations": locations
    }


@router.get("/search/{query}")
async def search_locations(query: str):
    """Search for locations using WeatherAPI"""
    try:
        locations = await weather_api_service.search_locations(query)
        return {
            "status": "success",
            "query": query,
            "results": [location.dict() for location in locations]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search locations: {str(e)}")


@router.get("/current-raw/{location}")
async def get_current_weather_raw(location: str):
    """Get current weather from WeatherAPI without saving to database"""
    try:
        weather_data = await weather_api_service.get_current_weather(location)
        return weather_data.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current weather: {str(e)}")


@router.get("/forecast-raw/{location}")
async def get_forecast_weather_raw(
    location: str,
    days: int = Query(default=3, ge=1, le=14)
):
    """Get weather forecast from WeatherAPI without saving to database"""
    try:
        forecast_data = await weather_api_service.get_forecast(location, days)
        return forecast_data.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get forecast weather: {str(e)}")


@router.get("/history-raw/{location}")
async def get_historical_weather_raw(
    location: str,
    dt: date = Query(description="Date (YYYY-MM-DD)")
):
    """Get historical weather from WeatherAPI without saving to database"""
    if dt > date.today():
        raise HTTPException(status_code=400, detail="Date cannot be in the future")
    
    try:
        history_data = await weather_api_service.get_history(location, dt)
        return history_data.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get historical weather: {str(e)}")
