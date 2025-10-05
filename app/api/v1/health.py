from fastapi import APIRouter, Request, HTTPException


health_router = APIRouter(prefix="/health", tags=["health"])

@health_router.post("")
async def health_check(request: Request):
    """
    Health check endpoint to verify the service is running
    """
    try:
        # Check database connection here if needed
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")