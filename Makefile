.PHONY: up down build migrate ingest setup test logs

up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build backend

migrate:
	docker compose run --rm backend alembic upgrade head

ingest:
	docker compose run --rm backend python -m app.ingestion.run

setup: migrate ingest

test:
	docker compose run --rm backend pytest -v
	docker compose stop db-test

logs:
	docker compose logs -f backend
