import os
from enum import Enum

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

current_file_dir = os.path.dirname(os.path.realpath(__file__))
env_path = os.path.join(current_file_dir, "..", "..", ".env")
load_dotenv(env_path)

class CrawlSettings(BaseSettings):
    key : str = os.getenv("WEATHER_API_KEY", "XXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX")
    crawl_base_url: str = os.getenv("CRAWL_BASE_URL", "http://crawl.weather/api/v1/")

class DatabaseSettings(BaseSettings):
    pass

class ClickHouseSettings(DatabaseSettings):
    host: str = os.getenv("CLICKHOUSE_HOST", "localhost")
    port: int = int(os.getenv("CLICKHOUSE_PORT", 8123))
    user: str = os.getenv("CLICKHOUSE_USER", "default")
    password: str = os.getenv("CLICKHOUSE_PASSWORD", "")
    db: str = os.getenv("CLICKHOUSE_DB", "default")
    
class ProjectSettings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "FAST API")
    DB: str = os.getenv("DB", "weather")
    

class Settings(ProjectSettings, ClickHouseSettings, CrawlSettings):
    pass

settings = Settings()