from pydantic_settings import BaseSettings


class ClickHouseSettings(BaseSettings):
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: str = "8123"
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = ""
    DB: str = "default"

class TelegramBotSettings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = "XXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"

class ProjectSettings(BaseSettings):
    PROJECT_NAME: str = "FAST API"


class Settings(ProjectSettings, ClickHouseSettings, TelegramBotSettings):
    pass

settings = Settings()
