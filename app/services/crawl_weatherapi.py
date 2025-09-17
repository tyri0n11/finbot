import requests

from fastapi import HTTPException
from services.insert_weather import insert_weather

from model.weather import parse_weather
from core.database import get_db
from core.settings import Settings


key = Settings().WEATHER_API_KEY
base_url = Settings().CRAWL_BASE_URL
lang = "vi"

def get_current_by_location(location: str):
    url = f"{base_url}current.json"
    
    params = {
        "q": location,
        "lang": lang,
        "key": key
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        weather_model = parse_weather(response.json())
        insert_weather(client=get_db(), data=weather_model)

        return {
            "status_code": response.status_code,
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")