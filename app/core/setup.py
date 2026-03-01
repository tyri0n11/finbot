from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from core.settings import Settings
from core.database import Database
from core.logger import get_logger
from core.context import set_db
import asyncio
from core.webhook import WebhookManager
from core.scheduler import NotificationScheduler
from repo.user_repo import UserRepository
from repo.message_repo import MessageRepository
from repo.command_log_repo import CommandLogRepository
from repo.subscription_repo import SubscriptionRepository


def init_databases() -> Database | None:
    """Initialize databases on application startup"""
    logger = get_logger()
    logger.info("Initializing databases...")
    try:
        db = Database()
        logger.info("Databases initialized successfully")
        return db
    except Exception as e:
        logger.error(f"Failed to initialize databases: {e}")
        return None


def create_application(router: APIRouter, settings: Settings) -> FastAPI:
    """Factory function tạo FastAPI app"""
    app = FastAPI(title=settings.PROJECT_NAME)

    monitor_task: asyncio.Task | None = None
    scheduler_task: asyncio.Task | None = None

    @app.on_event("startup")
    async def startup_event():
        db = init_databases()
        set_db(db)
        if db:
            # Order matters: users must exist before tables with FK to users
            UserRepository(db).init_schema()
            MessageRepository(db).init_schema()
            CommandLogRepository(db).init_schema()
            SubscriptionRepository(db).init_schema()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    # Webhook monitor background task
    manager = WebhookManager()

    @app.on_event("startup")
    async def _start_webhook_monitor() -> None:
        nonlocal monitor_task
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

    # Notification scheduler background task
    @app.on_event("startup")
    async def _start_scheduler() -> None:
        nonlocal scheduler_task
        from core.context import get_db
        db = get_db()
        if db:
            scheduler = NotificationScheduler(db)
            scheduler_task = asyncio.create_task(scheduler.run())

    @app.on_event("shutdown")
    async def _stop_scheduler() -> None:
        nonlocal scheduler_task
        if scheduler_task and not scheduler_task.done():
            scheduler_task.cancel()
            try:
                await scheduler_task
            except asyncio.CancelledError:
                pass

    return app
