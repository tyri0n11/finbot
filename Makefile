FORMAT = black . --exclude '(storage|migrations)'

# Default compose file (basic setup)
COMPOSE_FILE := compose.yaml
# Traefik compose file (with API Gateway)
TRAEFIK_COMPOSE_FILE := docker-compose-traefik.yaml

# ===========================================
# Basic Commands (using default compose)
# ===========================================

format:
	$(FORMAT)

up:
	docker compose -f $(COMPOSE_FILE) up -d --build

down:
	docker compose -f $(COMPOSE_FILE) down

restart: down up

logs:
	docker compose -f $(COMPOSE_FILE) logs -f

ps:
	docker compose -f $(COMPOSE_FILE) ps

build:
	docker compose -f $(COMPOSE_FILE) build

# ===========================================
# Traefik Commands (with API Gateway)
# ===========================================

traefik-up:
	docker compose -f $(TRAEFIK_COMPOSE_FILE) up -d --build

traefik-down:
	docker compose -f $(TRAEFIK_COMPOSE_FILE) down

traefik-restart: traefik-down traefik-up

traefik-logs:
	docker compose -f $(TRAEFIK_COMPOSE_FILE) logs -f

traefik-ps:
	docker compose -f $(TRAEFIK_COMPOSE_FILE) ps

# Start only essential services (no Traefik proxy)
traefik-backend-only:
	docker compose -f $(TRAEFIK_COMPOSE_FILE) up -d --build weather-backend clickhouse

# ===========================================
# Testing Commands
# ===========================================

test-health:
	curl -X GET "http://localhost:8000/automation/health" | jq .

test-crawl:
	curl -X POST "http://localhost:8000/automation/crawl" \
		-H "Content-Type: application/json" \
		-d '{"location": "Ho Chi Minh City"}' | jq .

test-traefik-crawl:
	curl -X POST "http://localhost:8080/api/v1/weather/automation/crawl" \
		-H "Content-Type: application/json" \
		-d '{"location": "Ho Chi Minh City"}' | jq .

# ===========================================
# Database Commands  
# ===========================================

db-check:
	docker compose -f $(COMPOSE_FILE) exec clickhouse clickhouse-client --query "SHOW DATABASES"

db-tables:
	docker compose -f $(COMPOSE_FILE) exec clickhouse clickhouse-client --query "USE weather; SHOW TABLES"

db-data:
	docker compose -f $(COMPOSE_FILE) exec clickhouse clickhouse-client --query "USE weather; SELECT * FROM weather_data ORDER BY created_at DESC LIMIT 10"

db-query:
	docker compose -f $(COMPOSE_FILE) exec clickhouse clickhouse-client --query "$(QUERY)"

# ===========================================
# Utility Commands
# ===========================================

clean:
	docker system prune -f
	docker volume prune -f

clean-all: down traefik-down clean

# Check logs for specific service
logs-weather:
	docker compose -f $(COMPOSE_FILE) logs -f weather-backend

logs-clickhouse:
	docker compose -f $(COMPOSE_FILE) logs -f clickhouse

# ===========================================
# Development Commands
# ===========================================

dev: up logs

dev-traefik: traefik-up traefik-logs

# ===========================================
# Legacy Commands (for backward compatibility)
# ===========================================

prune: clean

makemigrations:
	docker compose -f $(COMPOSE_FILE) exec backend_service alembic --config migrations/alembic.ini revision --autogenerate -m "$$MSG"

migrate:
	docker compose -f $(COMPOSE_FILE) exec backend_service alembic --config migrations/alembic.ini upgrade head

celery:
	docker compose -f $(COMPOSE_FILE) exec celery_worker bash

redis-cli:
	docker compose -f $(COMPOSE_FILE) exec redis redis-cli

# ===========================================
# Help Command
# ===========================================

help:
	@echo "Weather Backend Management Commands"
	@echo "=================================="
	@echo ""
	@echo "Basic Setup:"
	@echo "  up              - Start basic services (weather + clickhouse)"
	@echo "  down            - Stop basic services"  
	@echo "  restart         - Restart basic services"
	@echo "  logs            - View logs for basic services"
	@echo "  ps              - Show running containers"
	@echo ""
	@echo "Traefik Setup (with API Gateway):"
	@echo "  traefik-up      - Start all services with Traefik"
	@echo "  traefik-down    - Stop Traefik setup"
	@echo "  traefik-restart - Restart Traefik setup"
	@echo "  traefik-logs    - View Traefik logs"
	@echo "  traefik-backend-only - Start only backend services"
	@echo ""
	@echo "Testing:"
	@echo "  test-health     - Test health endpoint (direct)"
	@echo "  test-crawl      - Test crawl endpoint (direct)"
	@echo "  test-traefik-crawl - Test crawl via Traefik"
	@echo ""
	@echo "Database:"
	@echo "  db-check        - Check ClickHouse databases"
	@echo "  db-tables       - List weather tables"
	@echo "  db-data         - Show recent weather data"
	@echo "  db-query QUERY='...' - Run custom ClickHouse query"
	@echo ""
	@echo "Utilities:"
	@echo "  clean           - Clean unused Docker resources"
	@echo "  clean-all       - Stop all services and clean"
	@echo "  dev             - Start and follow logs (basic)"
	@echo "  dev-traefik     - Start and follow logs (traefik)"