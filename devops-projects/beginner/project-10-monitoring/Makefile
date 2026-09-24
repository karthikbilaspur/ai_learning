.PHONY: up down build logs test clean

## Start the full stack (app + nginx + prometheus + grafana)
up:
	docker compose up --build

## Same as up, but runs in the background
up-d:
	docker compose up -d --build

## Stop and remove containers
down:
	docker compose down

## Stop containers and delete volumes too (Grafana dashboards will be lost)
clean:
	docker compose down -v

## Build the app image only, without starting anything
build:
	docker build -t devops-starter:local .

## Follow logs from every service
logs:
	docker compose logs -f

## Run the test suite locally (needs: pip install -r requirements.txt)
test:
	pytest -q
