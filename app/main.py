from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import weather, automation, n8n

app = FastAPI(
    title="Weather API",
    description="A comprehensive weather data API using ClickHouse with automation support",
    version="1.0.0"
)

# Add CORS middleware for API Gateway integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this based on your API Gateway domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(weather.router)
app.include_router(automation.router)
app.include_router(n8n.router)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Weather API",
        "description": "Automation-ready weather service with ClickHouse storage",
        "endpoints": {
            "weather_crud": "/weather",
            "automation": "/automation", 
            "n8n_telegram": "/n8n",
            "docs": "/docs"
        },
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "services": ["weather", "automation", "n8n"],
        "database": "clickhouse"
    }