from core.settings import settings
import clickhouse_connect
from core.logger import get_logger
TAG = "Database"
class Database:
    def __init__(self):
        self.logger = get_logger()
        self.logger.info(f"[{TAG}] Connecting to ClickHouse at {settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT} with user {settings.CLICKHOUSE_USER}")
        self.client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST,
            port=int(settings.CLICKHOUSE_PORT) if settings.CLICKHOUSE_PORT is not None else None,
            username=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD,
            database=settings.DB
        )
    
    def get_session(self):
        return self.client

