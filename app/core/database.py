from core.settings import settings
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from core.logger import get_logger

TAG = "Database"


class Database:
    def __init__(self):
        self.logger = get_logger()

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

    def get_postgres_connection(self):
        """Get PostgreSQL connection from pool"""
        if self.postgres_pool:
            return self.postgres_pool.getconn()
        self.logger.error(f"[{TAG}] PostgreSQL connection pool not available")
        return None

    def return_postgres_connection(self, conn):
        """Return PostgreSQL connection to pool"""
        if self.postgres_pool and conn:
            self.postgres_pool.putconn(conn)

    def check_health(self):
        """Check PostgreSQL connection health"""
        health_status = {"postgresql": {"status": "unhealthy", "error": None, "details": None}}
        conn = None
        try:
            conn = self.get_postgres_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    cur.fetchone()
                health_status["postgresql"]["status"] = "healthy"
                health_status["postgresql"]["details"] = f"Database '{settings.POSTGRES_DB}' accessible"
                self.logger.info(f"[{TAG}] PostgreSQL health check passed")
            else:
                health_status["postgresql"]["error"] = "Connection pool unavailable"
        except Exception as e:
            health_status["postgresql"]["error"] = str(e)
            self.logger.error(f"[{TAG}] PostgreSQL health check failed: {e}")
        finally:
            if conn:
                self.return_postgres_connection(conn)

        health_status["overall"] = "healthy" if health_status["postgresql"]["status"] == "healthy" else "unhealthy"
        return health_status

    def close_connections(self):
        """Close all database connections"""
        if self.postgres_pool:
            self.postgres_pool.closeall()
            self.logger.info(f"[{TAG}] PostgreSQL connections closed")
