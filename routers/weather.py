from typing import List
from fastapi import APIRouter, HTTPException, Query
from models.weather import WeatherCreate, WeatherUpdate, WeatherResponse
from services.weather_service import weather_service

router = APIRouter(prefix="/weather", tags=["weather"])


@router.post("/", response_model=WeatherResponse)
async def create_weather(weather_data: WeatherCreate):
    """Create a new weather record"""
    try:
        return weather_service.create_weather(weather_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create weather record: {str(e)}")


@router.get("/", response_model=List[WeatherResponse])
async def get_weather_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get list of weather records"""
    try:
        return weather_service.get_weather_list(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather records: {str(e)}")


@router.get("/{weather_id}", response_model=WeatherResponse)
async def get_weather(weather_id: int):
    """Get weather record by ID"""
    try:
        weather = weather_service.get_weather(weather_id)
        if not weather:
            raise HTTPException(status_code=404, detail="Weather record not found")
        return weather
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather record: {str(e)}")


@router.put("/{weather_id}", response_model=WeatherResponse)
async def update_weather(weather_id: int, weather_update: WeatherUpdate):
    """Update weather record"""
    try:
        updated_weather = weather_service.update_weather(weather_id, weather_update)
        if not updated_weather:
            raise HTTPException(status_code=404, detail="Weather record not found")
        return updated_weather
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update weather record: {str(e)}")


@router.delete("/{weather_id}")
async def delete_weather(weather_id: int):
    """Delete weather record"""
    try:
        success = weather_service.delete_weather(weather_id)
        if not success:
            raise HTTPException(status_code=404, detail="Weather record not found or failed to delete")
        return {"message": "Weather record deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete weather record: {str(e)}")


@router.get("/location/{location}", response_model=List[WeatherResponse])
async def get_weather_by_location(
    location: str,
    limit: int = Query(10, ge=1, le=100)
):
    """Get weather records by location"""
    try:
        return weather_service.get_weather_by_location(location, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather records: {str(e)}")
