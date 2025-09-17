from core.settings import settings
import clickhouse_connect

client = clickhouse_connect.get_client(
    host=settings.CLICKHOUSE_HOST,
    port=settings.CLICKHOUSE_PORT,
    username=settings.CLICKHOUSE_USER,
    password=settings.CLICKHOUSE_PASSWORD,
    # database=settings.DB
    database='test'
)

def get_db():
    return client