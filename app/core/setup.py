from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from core.settings import ClickHouseSettings, ProjectSettings, Settings
from typing import Set, Union

SettingType = Union[ProjectSettings, ClickHouseSettings, Settings]

def create_application(router: APIRouter, settings: SettingType) -> FastAPI:
    """
    Factory function tạo FastAPI app
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    return app
