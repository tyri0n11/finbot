from core.settings import settings
import clickhouse_connect
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from core.logger import get_logger

TAG = "Database"

class Database:
    def __init__(self):
        self.logger = get_logger()
        
        # Initialize ClickHouse connection
        self.logger.info(f"[{TAG}] Connecting to ClickHouse at {settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT} with user {settings.CLICKHOUSE_USER}")
        self.clickhouse_client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST,
            port=int(settings.CLICKHOUSE_PORT) if settings.CLICKHOUSE_PORT is not None else None,
            username=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD,
            database=settings.CLICKHOUSE_DB
        )
        
        # Initialize PostgreSQL connection pool
        self.logger.info(f"[{TAG}] Connecting to PostgreSQL at {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT} with user {settings.POSTGRES_USER}")
        try:
            self.postgres_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=settings.POSTGRES_HOST,
                port=int(settings.POSTGRES_PORT),
                database=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD
            )
            self.logger.info(f"[{TAG}] PostgreSQL connection pool created successfully")
        except psycopg2.Error as e:
            self.logger.error(f"[{TAG}] Failed to create PostgreSQL connection pool: {e}")
            self.postgres_pool = None
            raise
    
    def get_clickhouse_session(self):
        """Get ClickHouse client session"""
        return self.clickhouse_client
    
    def get_postgres_connection(self):
        """Get PostgreSQL connection from pool"""
        if self.postgres_pool:
            return self.postgres_pool.getconn()
        else:
            self.logger.error(f"[{TAG}] PostgreSQL connection pool not available")
            return None
    
    def return_postgres_connection(self, conn):
        """Return PostgreSQL connection to pool"""
        if self.postgres_pool and conn:
            self.postgres_pool.putconn(conn)
    
    def get_session(self):
        """Legacy method - returns ClickHouse session for backward compatibility"""
        return self.clickhouse_client
    
    def close_connections(self):
        """Close all database connections"""
        if self.postgres_pool:
            self.postgres_pool.closeall()
            self.logger.info(f"[{TAG}] PostgreSQL connections closed")
        
        if self.clickhouse_client:
            self.clickhouse_client.close()
            self.logger.info(f"[{TAG}] ClickHouse connection closed")

