import core.database


class HealthService:
    def __init__(self):
        try:
            self.db = core.database.Database()
        except Exception as e:
            self.db = None
            self.init_error = str(e)

    def check_health(self):
        """Comprehensive health check including database connectivity"""
        try:
            if self.db is None:
                return {
                    "status": "unhealthy",
                    "service": "error",
                    "error": f"Database initialization failed: {getattr(self, 'init_error', 'Unknown error')}",
                    "databases": {
                        "postgresql": {"status": "unknown", "error": "Database service not initialized", "details": None}
                    },
                    "suggestions": ["Database service failed to initialize. Check database connectivity and configuration."]
                }

            db_health = self.db.check_health()
            health_status = {
                "status": "healthy" if db_health["overall"] == "healthy" else "unhealthy",
                "service": "healthy",
                "databases": {
                    "postgresql": db_health["postgresql"]
                }
            }

            if db_health["overall"] != "healthy":
                health_status["suggestions"] = ["PostgreSQL connection issue. Check if PostgreSQL container is running and credentials are correct."]

            return health_status

        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "error",
                "error": str(e),
                "databases": {
                    "postgresql": {"status": "unknown", "error": "Could not check", "details": None}
                },
                "suggestions": ["Service initialization failed. Check database configuration and connectivity."]
            }
