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

