from core.setup import create_application
from core.settings import settings
from api import router
from api.v1.webhook import webhook_router

app = create_application(router=router, settings=settings)

# Add webhook router directly to app (not under /api prefix)
app.include_router(webhook_router)