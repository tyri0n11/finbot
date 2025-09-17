from pydantic_settings import BaseSettings


class CrawlSettings(BaseSettings):
    WEATHER_API_KEY: str = "XXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    CRAWL_BASE_URL: str = "http://crawl.weather/api/v1/"


class ClickHouseSettings(BaseSettings):
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = ""
    CLICKHOUSE_DB: str = "default"


class ProjectSettings(BaseSettings):
    PROJECT_NAME: str = "FAST API"
    DB: str = "weather"


class Settings(ProjectSettings, ClickHouseSettings, CrawlSettings):
    """App global settings, auto load from env or .env if available"""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
