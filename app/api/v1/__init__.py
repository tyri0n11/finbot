from fastapi import APIRouter
from api.v1.webhook import webhook_router
from api.v1.health import health_router
router = APIRouter(prefix="/v1", tags=["v1"])

router.include_router(webhook_router)
router.include_router(health_router)