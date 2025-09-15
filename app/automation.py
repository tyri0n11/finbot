from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from services.weatherapi_simple import weatherapi_service

router = APIRouter(prefix="/automation", tags=["automation"])


class CrawlRequest(BaseModel):
    location: str
    days: int = 3
    include_current: bool = True
    include_forecast: bool = True


@router.post("/crawl")
async def crawl_weather_data(crawl_request: CrawlRequest):
    """
    API for automation engine to trigger weather data crawling
    This will fetch weather data from WeatherAPI.com and store in ClickHouse
    """
    try:
        result = await weatherapi_service.crawl_and_store(
            location=crawl_request.location,
            include_current=crawl_request.include_current,
            include_forecast=crawl_request.include_forecast,
            days=crawl_request.days
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawling failed: {str(e)}")


@router.post("/crawl-batch")
async def crawl_multiple_locations(crawl_requests: List[CrawlRequest]):
    """
    Batch crawl multiple locations at once
    """
    results = []
    for request in crawl_requests:
        try:
            result = await weatherapi_service.crawl_and_store(
                location=request.location,
                include_current=request.include_current,
                include_forecast=request.include_forecast,
                days=request.days
            )
            results.append(result)
        except Exception as e:
            results.append({
                "success": False,
                "message": f"Error: {str(e)}",
                "location": request.location,
                "records_created": 0
            })
    return results


@router.post("/crawl-async")
async def crawl_weather_data_async(crawl_request: CrawlRequest, background_tasks: BackgroundTasks):
    """
    Asynchronous crawling - returns immediately while processing in background
    """
    def crawl_in_background():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(weatherapi_service.crawl_and_store(
            location=crawl_request.location,
            include_current=crawl_request.include_current,
            include_forecast=crawl_request.include_forecast,
            days=crawl_request.days
        ))
        loop.close()
    
    background_tasks.add_task(crawl_in_background)
    return {
        "message": f"Started crawling weather data for {crawl_request.location}",
        "status": "processing"
    }
