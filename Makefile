FORMAT = black . --exclude '(storage|migrations)'

# Default compose file (basic setup)
COMPOSE_FILE := compose.yaml


# ===========================================
# Basic Commands (using default compose)
# ===========================================

format:
	$(FORMAT)

up:
	docker compose -f $(COMPOSE_FILE) up -d --build
	@sleep 5
	@./scripts/set_webhook.sh
down:
	docker compose -f $(COMPOSE_FILE) down

restart: down up

logs:
	docker compose -f $(COMPOSE_FILE) logs -f

ps:
	docker compose -f $(COMPOSE_FILE) ps

build:
	docker compose -f $(COMPOSE_FILE) build

