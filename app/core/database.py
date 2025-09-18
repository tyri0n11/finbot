from core.settings import settings
import clickhouse_connect
import logging
class Database:
    def __init__(self):
        logging.debug("%s", f"Connecting to ClickHouse at {settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT} with user {settings.CLICKHOUSE_USER}")
        self.client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST,
            port=int(settings.CLICKHOUSE_PORT) if settings.CLICKHOUSE_PORT is not None else None,
            username=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD,
            database=settings.DB
        )
    
    def get_session(self):
        return self.client

