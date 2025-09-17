from fastapi import APIRouter
from crawl import crawl_router

router = APIRouter(prefix="/v1", tags=["v1"])

router.include_router(crawl_router)