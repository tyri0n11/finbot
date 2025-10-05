import core.database 

class HealthService:
    def __init__(self):
        try:
            self.db = core.database.Database()
        except Exception as e:
            # If database initialization fails, we'll handle it in check_health
            self.db = None
            self.init_error = str(e)

    def check_health(self):
        """
        Comprehensive health check including database connectivity
        """
        try:
            # Check if database was initialized during service startup
            if self.db is None:
                return {
                    "status": "unhealthy",
                    "service": "error",
                    "error": f"Database initialization failed: {getattr(self, 'init_error', 'Unknown error')}",
                    "databases": {
                        "clickhouse": {"status": "unknown", "error": "Database service not initialized", "details": None},
                        "postgresql": {"status": "unknown", "error": "Database service not initialized", "details": None}
                    },
                    "suggestions": ["Database service failed to initialize. Check database connectivity and configuration."]
                }
            
            # Get database health status
            db_health = self.db.check_health()
            
            # Combine service and database health
            health_status = {
                "status": "healthy" if db_health["overall"] == "healthy" else "unhealthy",
                "service": "healthy",
                "databases": {
                    "clickhouse": db_health["clickhouse"],
                    "postgresql": db_health["postgresql"]
                }
            }
            
            # Add suggestions for fixing issues
            if db_health["overall"] != "healthy":
                suggestions = []
                
                if db_health["clickhouse"]["status"] != "healthy":
                    if "does not exist" in str(db_health["clickhouse"].get("error", "")):
                        suggestions.append("ClickHouse database needs to be created. Use create_clickhouse_database() method or create manually.")
                    elif "Connection failed" in str(db_health["clickhouse"].get("error", "")):
                        suggestions.append("ClickHouse server is not accessible. Check if ClickHouse container is running.")
                
                if db_health["postgresql"]["status"] != "healthy":
                    suggestions.append("PostgreSQL connection issue. Check if PostgreSQL container is running and credentials are correct.")
                
                health_status["suggestions"] = suggestions
            
            return health_status
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "error",
                "error": str(e),
                "databases": {
                    "clickhouse": {"status": "unknown", "error": "Could not check", "details": None},
                    "postgresql": {"status": "unknown", "error": "Could not check", "details": None}
                },
                "suggestions": ["Service initialization failed. Check database configuration and connectivity."]
            }