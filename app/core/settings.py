from pydantic_settings import BaseSettings


class PostgreSQLSettings(BaseSettings):
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres_user"
    POSTGRES_PASSWORD: str = "postgres_password"
    POSTGRES_DB: str = "postgres_db"


class TelegramBotSettings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = "XXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"


class ProjectSettings(BaseSettings):
    PROJECT_NAME: str = "FAST API"


class WebHookSettings(BaseSettings):
    NGROK_API: str = "http://ngrok:XXXX/api/tunnels"


class NotificationSettings(BaseSettings):
    OPENWEATHER_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    WEATHER_CITY: str = "Ho Chi Minh City"
    TIMEZONE: str = "Asia/Ho_Chi_Minh"


class Settings(ProjectSettings, PostgreSQLSettings, TelegramBotSettings, WebHookSettings, NotificationSettings):
    pass


settings = Settings()
