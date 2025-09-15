FORMAT = black . --exclude '(storage|migrations)'
COMPOSE_FILE := compose.yaml
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

prune:
	docker system prune -f

makemigrations:
	docker compose -f $(COMPOSE_FILE) exec backend_service alembic --config migrations/alembic.ini revision --autogenerate -m "$$MSG"

migrate:
	docker compose -f $(COMPOSE_FILE) exec backend_service alembic --config migrations/alembic.ini upgrade head


celery:
	docker compose -f $(COMPOSE_FILE) exec celery_worker bash

redis-cli:
	docker compose -f $(COMPOSE_FILE) exec redis redis-cli