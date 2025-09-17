from core.setup import create_application
from core.settings import settings
from api import router

app = create_application(router=router, settings=settings)