from pydantic_settings import BaseSettings


class ClickHouseSettings(BaseSettings):
    CLICKHOUSE_HOST: str = "clickhouse"
    CLICKHOUSE_PORT: str = "XXXX"
    CLICKHOUSE_USER: str = "clickhouse_user"
    CLICKHOUSE_PASSWORD: str = "clickhouse_password"
    CLICKHOUSE_DB: str = "clickhouse_db"

class PostgreSQLSettings(BaseSettings):
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: str = "XXXX"
    POSTGRES_USER: str = "postgres_user"
    POSTGRES_PASSWORD: str = "postgres_password"
    POSTGRES_DB: str = "postgres_db"


class TelegramBotSettings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = "XXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"

class ProjectSettings(BaseSettings):
    PROJECT_NAME: str = "FAST API"

class WebHookSettings(BaseSettings):
    NGROK_API: str = "http://ngrok:XXXX/api/tunnels"
    

class Settings(ProjectSettings, ClickHouseSettings, PostgreSQLSettings, TelegramBotSettings, WebHookSettings):
    pass

settings = Settings()
