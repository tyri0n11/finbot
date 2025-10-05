from fastapi import APIRouter, Request, HTTPException
from services.webhook import WebhookService

webhook_router = APIRouter(prefix="/webhook", tags=["webhook"])

# Initialize the webhook service
webhook_service = WebhookService()

@webhook_router.post("")
async def telegram_webhook(request: Request):
    """
    Handle incoming Telegram webhook updates
    """
    try:
        update_data = await request.json()

        if not webhook_service.validate_update(update_data):
            raise HTTPException(status_code=400, detail="Invalid update data")
        await webhook_service.process_update(update_data)

        return {"status": "ok"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")