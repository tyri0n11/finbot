from fastapi import APIRouter

from services.crawl_weatherapi import get_current_by_location

crawl_router = APIRouter(prefix="/crawl" , tags=["crawl"])


@crawl_router.get("/current", tags=["crawl"])
def get_current_weather(location: str):
    return get_current_by_location(location)