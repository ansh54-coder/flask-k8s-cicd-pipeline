.PHONY: install dev test lint format migrate upgrade seed \
        docker-build docker-up docker-down run

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

dev:
	flask --app app.main run --host=0.0.0.0 --port=5000 --debug

test:
	pytest

coverage:
	pytest --cov=app --cov-report=term-missing --cov-report=html

lint:
	flake8 app tests
	black --check app tests
	isort --check-only app tests

format:
	black app tests
	isort app tests

migrate:
	flask --app app.main db migrate -m "$(message)"

upgrade:
	flask --app app.main db upgrade

downgrade:
	flask --app app.main db downgrade -1

seed:
	python scripts/seed_db.py

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f api

run:
	docker compose up --build
