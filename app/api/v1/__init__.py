from fastapi import APIRouter
from api.v1.webhook import webhook_router

router = APIRouter(prefix="/v1", tags=["v1"])

router.include_router(webhook_router)