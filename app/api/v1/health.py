from fastapi import APIRouter, Request, HTTPException, status
from services.health import HealthService

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("")
async def health_check(request: Request):
    """Health check endpoint to verify the service and database connections"""
    try:
        health_service = HealthService()
        health_status = health_service.check_health()

        if health_status["status"] == "healthy":
            return health_status
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_status
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "unhealthy",
                "service": "error",
                "error": str(e),
                "databases": {
                    "postgresql": {"status": "unknown", "error": "Could not check", "details": None}
                },
                "suggestions": ["Unexpected error occurred during health check."]
            }
        )
