import requests
from fastapi import HTTPException
from core.settings import Settings
import logging


key = Settings().key
base_url = Settings().crawl_base_url
lang = "vi"
logger = logging.getLogger(__name__)

def get_current_by_location(location: str):
    url = f"{base_url}/current.json"
    
    params = {
        "q": location,
        "lang": lang,
        "key": key
    }
    try:
        logger.debug(f"Requesting URL: {url} with params: {params}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        logger.debug(f"Response: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")