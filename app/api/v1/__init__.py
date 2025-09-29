from fastapi import APIRouter
# from api.v1.crawl import crawl_router

router = APIRouter(prefix="/v1", tags=["v1"])

# router.include_router(crawl_router)