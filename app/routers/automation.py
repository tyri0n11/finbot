from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.simple_weatherapi import CrawlRequest, CrawlResponse
from services.simple_weatherapi_service import simple_weatherapi_service

router = APIRouter(prefix="/automation", tags=["automation"])


@router.post("/crawl", response_model=CrawlResponse)
async def crawl_weather_data(request: dict):
    """
    API for automation engine to trigger weather data crawling
    This will fetch weather data from WeatherAPI.com and store in ClickHouse
    """
    try:
        # Simple request - just need location
        location = request.get("location", "")
        if not location:
            raise HTTPException(status_code=400, detail="Location is required")
        
        # Create crawl request with default values
        crawl_request = CrawlRequest(
            location=location,
            include_current=True,
            include_forecast=True,
            days=2
        )
        
        result = await simple_weatherapi_service.crawl_and_store(crawl_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawling failed: {str(e)}")


@router.post("/crawl-batch", response_model=List[CrawlResponse])
async def crawl_multiple_locations(crawl_requests: List[CrawlRequest]):
    """
    Batch crawl multiple locations at once
    """
    results = []
    for request in crawl_requests:
        try:
            result = await simple_weatherapi_service.crawl_and_store(request)
            results.append(result)
        except Exception as e:
            results.append(CrawlResponse(
                success=False,
                message=f"Error: {str(e)}",
                location=request.location,
                records_created=0
            ))
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
        loop.run_until_complete(simple_weatherapi_service.crawl_and_store(crawl_request))
        loop.close()
    
    background_tasks.add_task(crawl_in_background)
    return {
        "message": f"Started crawling weather data for {crawl_request.location}",
        "status": "processing"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": ["weather", "automation", "n8n"],
        "database": "clickhouse"
    }
