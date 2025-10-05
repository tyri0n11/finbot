from fastapi import APIRouter, Request, HTTPException, status
from services.health import HealthService
from core.database import Database

health_router = APIRouter(prefix="/health", tags=["health"])

@health_router.get("")
async def health_check(request: Request):
    """
    Health check endpoint to verify the service and database connections are running
    Returns JSON response with detailed health information
    """
    try:
        health_service = HealthService()
        health_status = health_service.check_health()
        
        # Return appropriate HTTP status based on health
        if health_status["status"] == "healthy":
            return health_status
        else:
            # Return unhealthy status with 503 Service Unavailable
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_status
            )
            
    except HTTPException:
        # Re-raise HTTPException as is
        raise
    except Exception as e:
        # Handle unexpected errors
        error_response = {
            "status": "unhealthy",
            "service": "error",
            "error": str(e),
            "databases": {
                "clickhouse": {"status": "unknown", "error": "Could not check", "details": None},
                "postgresql": {"status": "unknown", "error": "Could not check", "details": None}
            },
            "suggestions": ["Unexpected error occurred during health check."]
        }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response
        )

@health_router.post("/fix-clickhouse")
async def fix_clickhouse_database(request: Request):
    """
    Attempt to create ClickHouse database if it doesn't exist
    """
    try:
        db = Database()
        success = db.create_clickhouse_database()
        
        if success:
            return {
                "status": "success",
                "message": "ClickHouse database created/verified successfully",
                "action": "database_created"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "status": "failed",
                    "message": "Failed to create ClickHouse database",
                    "action": "database_creation_failed"
                }
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Error creating ClickHouse database: {str(e)}",
                "action": "database_creation_error"
            }
        )