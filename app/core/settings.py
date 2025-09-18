from pydantic_settings import BaseSettings


class CrawlSettings(BaseSettings):
    WEATHER_API_KEY: str = "XXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    CRAWL_BASE_URL: str = "http://crawl.weather/api/v1/"


class ClickHouseSettings(BaseSettings):
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: str = "8123"
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = ""
    DB: str = "default"


class ProjectSettings(BaseSettings):
    PROJECT_NAME: str = "FAST API"


class Settings(ProjectSettings, ClickHouseSettings, CrawlSettings):
    pass

settings = Settings()
