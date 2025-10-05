from core.settings import settings
import clickhouse_connect
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from core.logger import get_logger

TAG = "Database"

class Database:
    def __init__(self):
        self.logger = get_logger()
        
        self.logger.info(f"[{TAG}] Connecting to ClickHouse at {settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT} with user {settings.CLICKHOUSE_USER}")
        try:
            self.clickhouse_client = clickhouse_connect.get_client(
                host=settings.CLICKHOUSE_HOST,
                port=int(settings.CLICKHOUSE_PORT) if settings.CLICKHOUSE_PORT else None,
                username=settings.CLICKHOUSE_USER,
                password=settings.CLICKHOUSE_PASSWORD,
                database=settings.CLICKHOUSE_DB
            )
            self.logger.info(f"[{TAG}] ClickHouse connection established successfully")
        except Exception as e:
            self.logger.error(f"[{TAG}] Failed to connect to ClickHouse: {e}")
            self.clickhouse_client = None

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
    
    def check_health(self):
        """
        Check the health of both ClickHouse and PostgreSQL connections
        Returns a dictionary with health status for each database
        """
        health_status = {
            "clickhouse": {"status": "unhealthy", "error": None, "details": None},
            "postgresql": {"status": "unhealthy", "error": None, "details": None}
        }
        
        # Check ClickHouse health
        try:
            # First try to connect without specifying database
            basic_client = clickhouse_connect.get_client(
                host=settings.CLICKHOUSE_HOST,
                port=int(settings.CLICKHOUSE_PORT) if settings.CLICKHOUSE_PORT is not None else None,
                username=settings.CLICKHOUSE_USER,
                password=settings.CLICKHOUSE_PASSWORD
            )
            
            # Test basic connection
            result = basic_client.query("SELECT 1")
            if result:
                health_status["clickhouse"]["details"] = "Basic connection successful"
                
                # Now try to test database-specific connection
                try:
                    result = self.clickhouse_client.query("SELECT 1")
                    if result:
                        health_status["clickhouse"]["status"] = "healthy"
                        health_status["clickhouse"]["details"] = f"Database '{settings.CLICKHOUSE_DB}' accessible"
                        self.logger.info(f"[{TAG}] ClickHouse health check passed")
                except Exception as db_error:
                    # Database doesn't exist or access issue
                    if "does not exist" in str(db_error):
                        health_status["clickhouse"]["error"] = f"Database '{settings.CLICKHOUSE_DB}' does not exist"
                        health_status["clickhouse"]["details"] = "ClickHouse server is running but database needs to be created"
                    else:
                        health_status["clickhouse"]["error"] = f"Database access error: {str(db_error)}"
                        health_status["clickhouse"]["details"] = "ClickHouse server accessible but database connection failed"
                    self.logger.warning(f"[{TAG}] ClickHouse database check failed: {db_error}")
            
            basic_client.close()
            
        except Exception as e:
            health_status["clickhouse"]["error"] = f"Connection failed: {str(e)}"
            health_status["clickhouse"]["details"] = "Cannot connect to ClickHouse server"
            self.logger.error(f"[{TAG}] ClickHouse health check failed: {e}")
        
        # Check PostgreSQL health
        conn = None
        try:
            conn = self.get_postgres_connection()
            if conn:
                # Simple query to test PostgreSQL connection
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                if result:
                    health_status["postgresql"]["status"] = "healthy"
                    health_status["postgresql"]["details"] = f"Database '{settings.POSTGRES_DB}' accessible"
                    self.logger.info(f"[{TAG}] PostgreSQL health check passed")
            else:
                health_status["postgresql"]["error"] = "Connection pool unavailable"
                health_status["postgresql"]["details"] = "PostgreSQL connection pool not initialized"
        except Exception as e:
            health_status["postgresql"]["error"] = str(e)
            health_status["postgresql"]["details"] = "PostgreSQL connection or query failed"
            self.logger.error(f"[{TAG}] PostgreSQL health check failed: {e}")
        finally:
            if conn:
                self.return_postgres_connection(conn)
        
        # Overall health status
        overall_healthy = all(db["status"] == "healthy" for db in health_status.values())
        health_status["overall"] = "healthy" if overall_healthy else "unhealthy"
        
        return health_status
    
    def create_clickhouse_database(self):
        """
        Create ClickHouse database if it doesn't exist
        Returns True if successful, False otherwise
        """
        try:
            # Connect without specifying database
            basic_client = clickhouse_connect.get_client(
                host=settings.CLICKHOUSE_HOST,
                port=int(settings.CLICKHOUSE_PORT) if settings.CLICKHOUSE_PORT is not None else None,
                username=settings.CLICKHOUSE_USER,
                password=settings.CLICKHOUSE_PASSWORD
            )
            
            # Create database if it doesn't exist
            create_db_query = f"CREATE DATABASE IF NOT EXISTS {settings.CLICKHOUSE_DB}"
            basic_client.command(create_db_query)
            
            # Verify database was created
            databases = basic_client.query("SHOW DATABASES")
            db_list = [row[0] for row in databases.result_rows]
            
            basic_client.close()
            
            if settings.CLICKHOUSE_DB in db_list:
                self.logger.info(f"[{TAG}] ClickHouse database '{settings.CLICKHOUSE_DB}' created/verified successfully")
                return True
            else:
                self.logger.error(f"[{TAG}] Failed to create ClickHouse database '{settings.CLICKHOUSE_DB}'")
                return False
                
        except Exception as e:
            self.logger.error(f"[{TAG}] Failed to create ClickHouse database: {e}")
            return False
    
    def close_connections(self):
        """Close all database connections"""
        if self.postgres_pool:
            self.postgres_pool.closeall()
            self.logger.info(f"[{TAG}] PostgreSQL connections closed")
        
        if self.clickhouse_client:
            self.clickhouse_client.close()
            self.logger.info(f"[{TAG}] ClickHouse connection closed")

