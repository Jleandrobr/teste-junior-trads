.PHONY: env up down down-v build migrate ingest setup test logs

env:
	cp -n .env.example .env

up: env
	docker compose up -d --build

down:
	docker compose down

down-v:
	docker compose down -v

build:
	docker compose build

migrate:
	docker compose run --rm backend alembic upgrade head

ingest:
	docker compose run --rm backend python -m app.ingestion.run

setup: migrate ingest

test:
	docker compose run --rm backend pytest -v
	docker compose stop db-test

logs:
	docker compose logs -f
