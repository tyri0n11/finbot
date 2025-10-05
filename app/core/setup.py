from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from core.settings import ClickHouseSettings, ProjectSettings, Settings, TelegramBotSettings, WebHookSettings
from core.database import Database
from core.logger import get_logger
from typing import Set, Union
import asyncio
from core.webhook import WebhookManager

SettingType = Union[ProjectSettings, ClickHouseSettings, Settings, TelegramBotSettings, WebHookSettings]

def init_databases():
    """
    Initialize databases on application startup
    """
    logger = get_logger()
    logger.info("Initializing databases...")
    
    try:
        db = Database()
        logger.info("Databases initialized successfully")
        return db
    except Exception as e:
        logger.error(f"Failed to initialize databases: {e}")
        # Don't raise exception, let the app start and handle errors in health checks
        return None

def create_application(router: APIRouter, settings: SettingType) -> FastAPI:
    """
    Factory function tạo FastAPI app
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
    )

    # Initialize databases on startup
    @app.on_event("startup")
    async def startup_event():
        """Initialize databases when application starts"""
        init_databases()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    # set up webhook manager to run in background
    manager = WebhookManager()
    monitor_task: asyncio.Task | None = None

    @app.on_event("startup")
    async def _start_webhook_monitor() -> None:
        nonlocal monitor_task
        # run monitor_webhook as a background task
        monitor_task = asyncio.create_task(manager.monitor_webhook())

    @app.on_event("shutdown")
    async def _stop_webhook_monitor() -> None:
        nonlocal monitor_task
        if monitor_task and not monitor_task.done():
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass

    return app
